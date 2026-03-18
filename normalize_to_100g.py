import pandas as pd
import numpy as np

df = pd.read_csv('ramadan_dataset_cleaned.csv')

numeric_cols = ['calories', 'protein_g', 'fat_g', 'sat_fat_g',
                'carbs_g', 'fiber_g', 'sugars_g', 'sodium_mg']

# الصفوف اللي grams = 0 نحذفهم لأنه ما في وزن أصلي نقسم عليه
df = df[df['grams'] > 0].copy()

# نقسم كل قيمة على الوزن الأصلي ونضرب في 100
for col in numeric_cols:
    df[col] = (df[col] / df['grams'] * 100).round(2)

# نثبت grams على 100
df['grams'] = 100

print(f"✅ Rows after normalization: {len(df)}")
print(df[['food', 'grams', 'calories', 'protein_g', 'fat_g', 'carbs_g']].head(8).to_string(index=False))

df.to_csv('ramadan_100g.csv', index=False)
print("\n✅ Saved: ramadan_100g.csv")
