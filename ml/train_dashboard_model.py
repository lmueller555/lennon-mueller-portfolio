import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from tensorflow import keras
import json
from datetime import datetime

DATA_FILE = '../WA_Fn-UseC_-Telco-Customer-Churn.csv'

# Load dataset
data = pd.read_csv(DATA_FILE)

# Basic cleaning
data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')
if 'customerID' in data.columns:
    data = data.drop('customerID', axis=1)

data = data.dropna(subset=['Churn'])

X = data.drop('Churn', axis=1)
y = data['Churn'].map({'Yes': 1, 'No': 0})

numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
categorical_features = X.select_dtypes(include=['object']).columns

numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocess = ColumnTransformer([
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

X_processed = preprocess.fit_transform(X)

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(
    X_processed, y, test_size=0.4, stratify=y, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

# Build neural network
input_dim = X_train.shape[1]
model = keras.models.Sequential([
    keras.layers.Input(shape=(input_dim,)),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=keras.optimizers.Adam(3e-4),
    loss='binary_crossentropy',
    metrics=[keras.metrics.AUC(name='auc'),
             keras.metrics.Precision(name='precision'),
             keras.metrics.Recall(name='recall')]
)

early_stop = keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=10, restore_best_weights=True)

model.fit(
    X_train.toarray(), y_train,
    validation_data=(X_val.toarray(), y_val),
    epochs=100, batch_size=32,
    callbacks=[early_stop], verbose=0
)

metrics = model.evaluate(X_test.toarray(), y_test, verbose=0)
metrics_dict = {
    'auc': float(metrics[1]),
    'precision': float(metrics[2]),
    'recall': float(metrics[3]),
    'trained_at': datetime.utcnow().isoformat()
}

# Save model and preprocess objects
model.save('churn_model.h5')
import joblib
joblib.dump(preprocess, 'preprocess.pkl')

# Feature combination analysis
comb_data = data.copy()
comb_data['tenure_bin'] = pd.cut(comb_data['tenure'], bins=[0,12,24,48,72], labels=['0-12','12-24','24-48','48+'])
comb_data['charges_bin'] = pd.cut(comb_data['MonthlyCharges'], bins=[0,35,70,120], labels=['<35','35-70','70+'])

pairs = [
    ('Contract','TechSupport'),
    ('InternetService','PaymentMethod'),
    ('tenure_bin','charges_bin')
]

combo_records = []
for f1, f2 in pairs:
    g = comb_data.groupby([f1, f2])['Churn'].agg(['mean','count']).reset_index()
    g = g[g['count'] >= 20]
    for _, row in g.iterrows():
        combo_records.append({
            'features': [f1, f2],
            'values': [row[f1], row[f2]],
            'rate': float(row['mean']),
            'count': int(row['count'])
        })

combo_records = sorted(combo_records, key=lambda x: x['rate'])
lowest = combo_records[:5]
highest = combo_records[-5:][::-1]

combo_info = {
    'top_combos': highest,
    'bottom_combos': lowest,
    'total_customers': int(len(comb_data)),
    'churn_rate': float(y.mean())
}

with open('metrics.json', 'w') as f:
    json.dump(metrics_dict, f)

with open('combos.json', 'w') as f:
    json.dump(combo_info, f)
