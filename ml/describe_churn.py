import csv
from collections import defaultdict
import json

DATA_FILE = '../WA_Fn-UseC_-Telco-Customer-Churn.csv'

# Load rows
rows = []
with open(DATA_FILE, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row.get('Churn'):
            continue
        row['MonthlyCharges'] = float(row['MonthlyCharges']) if row['MonthlyCharges'] else None
        row['tenure'] = int(row['tenure']) if row['tenure'] else None
        rows.append(row)

def tenure_bin(val):
    if val is None:
        return None
    if val < 12:
        return '0-12'
    if val < 24:
        return '12-24'
    if val < 48:
        return '24-48'
    return '48+'

def charges_bin(val):
    if val is None:
        return None
    if val < 35:
        return '<35'
    if val < 70:
        return '35-70'
    return '70+'

for row in rows:
    row['tenure_bin'] = tenure_bin(row['tenure'])
    row['charges_bin'] = charges_bin(row['MonthlyCharges'])

pairs = [
    ('Contract','TechSupport'),
    ('InternetService','PaymentMethod'),
    ('tenure_bin','charges_bin')
]

records = []
for f1, f2 in pairs:
    agg = defaultdict(lambda: [0,0])
    for row in rows:
        a,b = row.get(f1), row.get(f2)
        if not a or not b:
            continue
        key = (a,b)
        churn = 1 if row['Churn'] == 'Yes' else 0
        agg[key][0] += churn
        agg[key][1] += 1
    for (a,b),(s,c) in agg.items():
        if c >= 20:
            records.append({'features':[f1,f2],'values':[a,b],'rate':s/c,'count':c})

records.sort(key=lambda x: x['rate'])
lowest = records[:5]
highest = records[-5:][::-1]

# Build a story from the highest combo
best = highest[0]
f1,f2 = best['features']
v1,v2 = best['values']
story = (
    f"Customers with {f1} = {v1} and {f2} = {v2} churn at "
    f"{best['rate']*100:.1f}% (n={best['count']})."
)

result = {
    'top_combos': highest,
    'bottom_combos': lowest,
    'total_customers': len(rows),
    'churn_rate': sum(1 for r in rows if r['Churn']=='Yes')/len(rows),
    'highest_rule': story
}

with open('../combos.json','w') as f:
    json.dump(result,f,indent=2)
