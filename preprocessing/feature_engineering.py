"""
Feature Engineering Pipeline for TelcoGuard
Includes: Data preprocessing, feature creation, and feature selection
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import warnings

warnings.filterwarnings('ignore')

print("=" * 100)
print("TELCGUARD: FEATURE ENGINEERING PIPELINE")
print("=" * 100)

# ======================== 1. LOAD DATA ========================
print("\n1. LOADING DATA...")
print("-" * 100)

df = pd.read_csv("data/telco_churn.csv")
print(f"✓ Data loaded: {df.shape}")
print(f"✓ Columns: {list(df.columns)}")

# ======================== 2. DATA QUALITY CHECKS ========================
print("\n2. DATA QUALITY CHECKS...")
print("-" * 100)

print(f"Missing values: {df.isnull().sum().sum()}")
print(f"Duplicate rows: {df.duplicated().sum()}")
print(f"Data types:\n{df.dtypes}")

# Handle any missing values
df = df.dropna()
df = df.drop_duplicates()

print(f"✓ After cleaning: {df.shape}")

# ======================== 3. FEATURE ENGINEERING ========================
print("\n3. CREATING ENGINEERED FEATURES...")
print("-" * 100)

df_features = df.copy()

# A. RATIO FEATURES
print("\n▶ Creating Ratio Features...")
df_features['avg_monthly_vs_total'] = df_features['monthly_charges'] / (df_features['total_charges'] + 1)
df_features['monthly_to_tenure_ratio'] = df_features['monthly_charges'] / (df_features['tenure'] + 1)
df_features['total_to_tenure_ratio'] = df_features['total_charges'] / (df_features['tenure'] + 1)
df_features['spending_growth'] = (df_features['monthly_charges'] - df_features['total_charges'] / (df_features['tenure'] + 1)) 
print("  ✓ Ratio features created")

# B. TENURE-BASED FEATURES
print("\n▶ Creating Tenure-Based Features...")
df_features['tenure_group'] = pd.cut(df_features['tenure'], 
                                     bins=[0, 12, 24, 48, 72], 
                                     labels=['0-12m', '12-24m', '24-48m', '48m+'])
df_features['is_new_customer'] = (df_features['tenure'] <= 12).astype(int)
df_features['is_established_customer'] = (df_features['tenure'] >= 48).astype(int)
df_features['tenure_squared'] = df_features['tenure'] ** 2
df_features['tenure_log'] = np.log1p(df_features['tenure'])
print("  ✓ Tenure features created")

# C. CHARGE-BASED FEATURES
print("\n▶ Creating Charge-Based Features...")
df_features['charge_per_month'] = df_features['total_charges'] / (df_features['tenure'] + 1)
df_features['high_charge'] = (df_features['monthly_charges'] > df_features['monthly_charges'].quantile(0.75)).astype(int)
df_features['low_charge'] = (df_features['monthly_charges'] < df_features['monthly_charges'].quantile(0.25)).astype(int)
df_features['charge_volatility'] = df_features['monthly_charges'] - df_features['charge_per_month']
print("  ✓ Charge features created")

# D. RISK INDICATORS
print("\n▶ Creating Risk Indicators...")
df_features['at_risk_new_high_cost'] = ((df_features['tenure'] <= 12) & 
                                        (df_features['monthly_charges'] > 100)).astype(int)
df_features['quick_churn_risk'] = ((df_features['total_charges'] / (df_features['monthly_charges'] + 1)) <= 24).astype(int)
df_features['sustained_loyalty'] = ((df_features['tenure'] >= 24) & 
                                    (df_features['monthly_charges'] > 50)).astype(int)
print("  ✓ Risk indicators created")

# E. SERVICE COUNT FEATURES (if available)
print("\n▶ Creating Service Features...")
service_cols = [col for col in df_features.columns if 'service' in col.lower() or 'phone' in col.lower() or 'streaming' in col.lower() or 'protection' in col.lower()]
if service_cols:
    df_features['service_count'] = df_features[service_cols].sum(axis=1)
    df_features['multi_service_user'] = (df_features['service_count'] >= 2).astype(int)
    print(f"  ✓ Service features created: {service_cols}")
else:
    print("  ℹ No service-related columns found")

# F. INTERACTION FEATURES
print("\n▶ Creating Interaction Features...")
df_features['tenure_charge_interaction'] = df_features['tenure'] * df_features['monthly_charges']
df_features['risk_value_ratio'] = df_features['at_risk_new_high_cost'] * df_features['monthly_charges']
print("  ✓ Interaction features created")

print(f"\n✓ Total features after engineering: {df_features.shape[1]}")
print(f"✓ New features created: {df_features.shape[1] - df.shape[1]}")

# ======================== 4. CATEGORICAL ENCODING ========================
print("\n4. ENCODING CATEGORICAL FEATURES...")
print("-" * 100)

categorical_cols = df_features.select_dtypes(include=['object']).columns
print(f"Categorical columns: {list(categorical_cols)}")

# Label encode target variable
if 'churn' in df_features.columns:
    le_target = LabelEncoder()
    df_features['churn'] = le_target.fit_transform(df_features['churn'])
    print(f"✓ Target encoded: churn -> {dict(zip(le_target.classes_, le_target.transform(le_target.classes_)))}")

# One-hot encode categorical features
for col in categorical_cols:
    if col not in ['tenure_group']:  # tenure_group is already categorical
        dummies = pd.get_dummies(df_features[col], prefix=col, drop_first=True)
        df_features = pd.concat([df_features, dummies], axis=1)
        df_features = df_features.drop(col, axis=1)
        print(f"✓ One-hot encoded: {col}")

# Handle tenure_group separately if present
if 'tenure_group' in df_features.columns:
    tenure_dummies = pd.get_dummies(df_features['tenure_group'], prefix='tenure_group', drop_first=True)
    df_features = pd.concat([df_features, tenure_dummies], axis=1)
    df_features = df_features.drop('tenure_group', axis=1)
    print(f"✓ One-hot encoded: tenure_group")

print(f"\n✓ Final feature count: {df_features.shape[1]}")

# ======================== 5. FEATURE SCALING ========================
print("\n5. FEATURE SCALING...")
print("-" * 100)

scaler = StandardScaler()
X = df_features.drop('churn', axis=1)
y = df_features['churn']

X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)

print(f"✓ Features scaled using StandardScaler")
print(f"✓ Shape after scaling: {X_scaled_df.shape}")

# ======================== 6. FEATURE SELECTION ========================
print("\n6. FEATURE SELECTION (SelectKBest)...")
print("-" * 100)

# Univariate feature selection
selector = SelectKBest(f_classif, k=20)
X_selected = selector.fit_transform(X_scaled_df, y)

selected_features = X_scaled_df.columns[selector.get_support()].tolist()
feature_scores = pd.DataFrame({
    'Feature': X_scaled_df.columns,
    'Score': selector.scores_
}).sort_values('Score', ascending=False)

print("\nTop 20 Features by F-Score:")
print(feature_scores.head(20).to_string(index=False))

# ======================== 7. FEATURE STATISTICS ========================
print("\n7. FEATURE STATISTICS...")
print("-" * 100)

print("\nFeature Summary:")
print(X_scaled_df.describe().to_string())

# ======================== 8. CORRELATION ANALYSIS ========================
print("\n8. CORRELATION WITH TARGET VARIABLE...")
print("-" * 100)

correlation_with_target = pd.DataFrame({
    'Feature': X.columns,
    'Correlation': [X[col].corr(y) for col in X.columns]
}).sort_values('Correlation', key=abs, ascending=False)

print("\nTop 15 Features by Correlation with Churn:")
print(correlation_with_target.head(15).to_string(index=False))

# ======================== 9. SAVE PREPROCESSED DATA ========================
print("\n9. SAVING PREPROCESSED DATA...")
print("-" * 100)

# Save full engineered dataset
df_features.to_csv('data/telco_churn_engineered.csv', index=False)
print("✓ Saved: data/telco_churn_engineered.csv")

# Save selected features dataset
X_selected_df = pd.DataFrame(X_selected, columns=selected_features)
X_selected_df['churn'] = y.values
X_selected_df.to_csv('data/telco_churn_selected_features.csv', index=False)
print("✓ Saved: data/telco_churn_selected_features.csv")

# Save feature mapping
feature_mapping = {
    'all_features': X.columns.tolist(),
    'selected_features': selected_features,
    'feature_scores': feature_scores.to_dict('records'),
    'correlation_with_target': correlation_with_target.to_dict('records')
}

import json
with open('model/feature_mapping.json', 'w') as f:
    json.dump(feature_mapping, f, indent=4)
print("✓ Saved: model/feature_mapping.json")

# ======================== 10. SUMMARY REPORT ========================
print("\n" + "=" * 100)
print("FEATURE ENGINEERING SUMMARY")
print("=" * 100)

print(f"\n📊 Dataset Overview:")
print(f"  • Original features: {df.shape[1]}")
print(f"  • Engineered features: {df_features.shape[1]}")
print(f"  • Selected features: {len(selected_features)}")
print(f"  • Total samples: {df_features.shape[0]}")

print(f"\n🔧 Features Created:")
print(f"  • Ratio features: 4")
print(f"  • Tenure-based features: 5")
print(f"  • Charge-based features: 4")
print(f"  • Risk indicators: 3")
print(f"  • Service features: 2 (if available)")
print(f"  • Interaction features: 2")

print(f"\n✨ Top 5 Features by Correlation:")
for idx, row in correlation_with_target.head(5).iterrows():
    print(f"  {row['Feature']}: {row['Correlation']:.4f}")

print("\n" + "=" * 100)
print("FEATURE ENGINEERING COMPLETE!")
print("=" * 100)
