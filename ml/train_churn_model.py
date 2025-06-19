import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from tensorflow import keras
import joblib
import json
from datetime import datetime

# Load dataset
DATA_FILE = '../WA_Fn-UseC_-Telco-Customer-Churn.csv'

data = pd.read_csv(DATA_FILE)

# Preprocess
data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')
# Drop customerID
if 'customerID' in data.columns:
    data = data.drop('customerID', axis=1)
# Drop rows with missing target
data = data.dropna(subset=['Churn'])

X = data.drop('Churn', axis=1)
y = data['Churn'].map({'Yes': 1, 'No': 0})

numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
text_features = X.select_dtypes(include=['object']).columns

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
    ('cat', categorical_transformer, text_features)
])

X_processed = preprocess.fit_transform(X)

# Train/val/test split
X_train, X_temp, y_train, y_temp = train_test_split(
    X_processed, y, test_size=0.4, stratify=y, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

input_dim = X_train.shape[1]
model = keras.models.Sequential([
    keras.layers.Input(shape=(input_dim,)),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.BatchNormalization(),
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

history = model.fit(
    X_train.toarray(), y_train,
    validation_data=(X_val.toarray(), y_val),
    epochs=100, batch_size=32,
    callbacks=[early_stop]
)

metrics = model.evaluate(X_test.toarray(), y_test, verbose=0)
metrics_dict = {
    'auc': float(metrics[1]),
    'precision': float(metrics[2]),
    'recall': float(metrics[3]),
    'trained_at': datetime.utcnow().isoformat()
}

with open('metrics.json', 'w') as f:
    json.dump(metrics_dict, f)

joblib.dump(preprocess, 'preprocess.pkl')
model.save('churn_model.h5')
