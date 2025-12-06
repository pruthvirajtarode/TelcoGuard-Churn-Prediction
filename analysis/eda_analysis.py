import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load data
df = pd.read_csv("data/telco_churn.csv")

print("=" * 80)
print("TELCGUARD: EXPLORATORY DATA ANALYSIS")
print("=" * 80)

# ======================== 1. DATA QUALITY REPORT ========================
print("\n1. DATA QUALITY REPORT")
print("-" * 80)
print(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nMissing Values:\n{df.isnull().sum()}")
print(f"Duplicate Rows: {df.duplicated().sum()}")
print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# ======================== 2. DESCRIPTIVE STATISTICS ========================
print("\n2. DESCRIPTIVE STATISTICS")
print("-" * 80)
print(df.describe())

# ======================== 3. DISTRIBUTION ANALYSIS ========================
print("\n3. DISTRIBUTION ANALYSIS")
print("-" * 80)

# Numerical columns analysis
numerical_cols = df.select_dtypes(include=[np.number]).columns
for col in numerical_cols:
    print(f"\n{col}:")
    print(f"  Mean: {df[col].mean():.2f}")
    print(f"  Median: {df[col].median():.2f}")
    print(f"  Std Dev: {df[col].std():.2f}")
    print(f"  Skewness: {df[col].skew():.4f}")
    print(f"  Kurtosis: {df[col].kurtosis():.4f}")

# Categorical analysis
categorical_cols = df.select_dtypes(include=['object']).columns
print("\nCategorical Columns:")
for col in categorical_cols:
    print(f"\n{col}:")
    print(df[col].value_counts())

# ======================== 4. VISUALIZATION: DISTRIBUTIONS ========================
print("\n4. CREATING DISTRIBUTION VISUALIZATIONS...")
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Feature Distributions', fontsize=16, fontweight='bold')

# Tenure distribution
axes[0, 0].hist(df['tenure'], bins=30, color='steelblue', edgecolor='black')
axes[0, 0].set_title('Tenure Distribution (months)', fontweight='bold')
axes[0, 0].set_xlabel('Tenure')
axes[0, 0].set_ylabel('Frequency')

# Monthly charges distribution
axes[0, 1].hist(df['monthly_charges'], bins=30, color='coral', edgecolor='black')
axes[0, 1].set_title('Monthly Charges Distribution', fontweight='bold')
axes[0, 1].set_xlabel('Monthly Charges (₹)')
axes[0, 1].set_ylabel('Frequency')

# Total charges distribution
axes[1, 0].hist(df['total_charges'], bins=30, color='lightgreen', edgecolor='black')
axes[1, 0].set_title('Total Charges Distribution', fontweight='bold')
axes[1, 0].set_xlabel('Total Charges (₹)')
axes[1, 0].set_ylabel('Frequency')

# Churn distribution
churn_counts = df['churn'].value_counts()
colors = ['#2ecc71', '#e74c3c']
axes[1, 1].bar(['Retained', 'Churned'], churn_counts.values, color=colors, edgecolor='black')
axes[1, 1].set_title('Churn Status Distribution', fontweight='bold')
axes[1, 1].set_ylabel('Count')
axes[1, 1].text(0, churn_counts.values[0]/2, f'{churn_counts.values[0]}\n({churn_counts.values[0]/len(df)*100:.1f}%)', 
                ha='center', va='center', fontweight='bold', fontsize=10)
axes[1, 1].text(1, churn_counts.values[1]/2, f'{churn_counts.values[1]}\n({churn_counts.values[1]/len(df)*100:.1f}%)', 
                ha='center', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('visualizations/01_distributions.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/01_distributions.png")
plt.close()

# ======================== 5. CORRELATION ANALYSIS ========================
print("\n5. CORRELATION ANALYSIS...")
correlation_matrix = df[numerical_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('visualizations/02_correlation_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/02_correlation_matrix.png")
plt.close()

# ======================== 6. CHURN ANALYSIS ========================
print("\n6. CHURN ANALYSIS")
print("-" * 80)

# Overall churn rate
churn_rate = (df['churn'].sum() / len(df)) * 100
print(f"Overall Churn Rate: {churn_rate:.2f}%")

# Churn by tenure groups
df['tenure_group'] = pd.cut(df['tenure'], bins=[0, 12, 24, 48, 72], 
                            labels=['0-12 months', '12-24 months', '24-48 months', '48+ months'])

churn_by_tenure = df.groupby('tenure_group', observed=True).agg({
    'churn': ['count', 'sum', 'mean']
}).round(4)
churn_by_tenure.columns = ['Total', 'Churned', 'Churn_Rate']
churn_by_tenure['Churn_Rate'] = churn_by_tenure['Churn_Rate'] * 100
print("\nChurn Rate by Tenure Group:")
print(churn_by_tenure)

# ======================== 7. BOX PLOTS BY CHURN ========================
print("\n7. CREATING BOX PLOTS BY CHURN STATUS...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Feature Distributions by Churn Status', fontsize=14, fontweight='bold')

features_to_plot = ['tenure', 'monthly_charges', 'total_charges']
for idx, feature in enumerate(features_to_plot):
    bp = axes[idx].boxplot([df[df['churn']==0][feature], df[df['churn']==1][feature]], 
                           labels=['Retained', 'Churned'],
                           patch_artist=True)
    bp['boxes'][0].set_facecolor('#2ecc71')
    bp['boxes'][1].set_facecolor('#e74c3c')
    axes[idx].set_title(f'{feature.title()}', fontweight='bold')
    axes[idx].set_ylabel(feature.title())
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/03_boxplots_by_churn.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/03_boxplots_by_churn.png")
plt.close()

# ======================== 8. VIOLIN PLOTS ========================
print("\n8. CREATING VIOLIN PLOTS...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Distribution Density by Churn Status', fontsize=14, fontweight='bold')

for idx, feature in enumerate(features_to_plot):
    data_retained = df[df['churn']==0][feature]
    data_churned = df[df['churn']==1][feature]
    
    parts = axes[idx].violinplot([data_retained, data_churned], positions=[1, 2],
                                 showmeans=True, showmedians=True)
    axes[idx].set_xticks([1, 2])
    axes[idx].set_xticklabels(['Retained', 'Churned'])
    axes[idx].set_title(f'{feature.title()} Distribution', fontweight='bold')
    axes[idx].set_ylabel(feature.title())
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/04_violin_plots.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/04_violin_plots.png")
plt.close()

# ======================== 9. CHURN TREND BY TENURE ========================
print("\n9. CREATING CHURN TREND ANALYSIS...")
fig, ax = plt.subplots(figsize=(14, 6))

tenure_churn = df.groupby('tenure_group', observed=True)['churn'].agg(['count', 'sum', 'mean']).reset_index()
tenure_churn['churn_rate'] = tenure_churn['mean'] * 100

colors_grad = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']
bars = ax.bar(tenure_churn['tenure_group'], tenure_churn['churn_rate'], color=colors_grad, edgecolor='black', linewidth=1.5)

ax.set_xlabel('Tenure Group', fontweight='bold', fontsize=12)
ax.set_ylabel('Churn Rate (%)', fontweight='bold', fontsize=12)
ax.set_title('Churn Rate by Tenure Group', fontweight='bold', fontsize=14)
ax.set_ylim(0, 100)

# Add value labels on bars
for idx, (bar, rate) in enumerate(zip(bars, tenure_churn['churn_rate'])):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{rate:.1f}%\n(n={int(tenure_churn["count"].iloc[idx])})',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('visualizations/05_churn_by_tenure.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/05_churn_by_tenure.png")
plt.close()

# ======================== 10. STATISTICAL TESTS ========================
print("\n10. STATISTICAL TESTS")
print("-" * 80)

# T-test: Tenure between Churned vs Retained
t_stat_tenure, p_val_tenure = stats.ttest_ind(df[df['churn']==0]['tenure'], 
                                              df[df['churn']==1]['tenure'])
print(f"\nT-Test for Tenure:")
print(f"  t-statistic: {t_stat_tenure:.4f}")
print(f"  p-value: {p_val_tenure:.4e}")
print(f"  Significant: {'Yes' if p_val_tenure < 0.05 else 'No'}")

# Chi-square test for categorical features
from scipy.stats import chi2_contingency

cat_features = ['internet_service_type', 'contract_type', 'tech_support']
for feature in cat_features:
    contingency_table = pd.crosstab(df[feature], df['churn'])
    chi2, p_val, dof, expected = chi2_contingency(contingency_table)
    print(f"\nChi-Square Test for {feature}:")
    print(f"  chi2-statistic: {chi2:.4f}")
    print(f"  p-value: {p_val:.4e}")
    print(f"  Significant: {'Yes' if p_val < 0.05 else 'No'}")

# ======================== 11. CUSTOMER SEGMENTATION ========================
print("\n11. CUSTOMER SEGMENTATION ANALYSIS")
print("-" * 80)

# Create segments
df['value_segment'] = pd.qcut(df['total_charges'], q=3, labels=['Low Value', 'Medium Value', 'High Value'])
df['risk_segment'] = pd.cut(df['tenure'], bins=[0, 12, 24, 72], 
                            labels=['High Risk (0-12mo)', 'Medium Risk (12-24mo)', 'Low Risk (24+mo)'])

segment_analysis = df.groupby(['value_segment', 'risk_segment']).agg({
    'churn': ['count', 'sum', 'mean']
}).round(4)
segment_analysis.columns = ['Total', 'Churned', 'Churn_Rate']
segment_analysis['Churn_Rate'] = segment_analysis['Churn_Rate'] * 100

print("\nCustomer Segmentation Matrix (Value × Risk):")
print(segment_analysis)

# ======================== 12. FEATURE ENGINEERING INSIGHTS ========================
print("\n12. FEATURE ENGINEERING OPPORTUNITIES")
print("-" * 80)

# Create derived features
df['avg_monthly_vs_total'] = df['monthly_charges'] / (df['total_charges'] + 1)
df['is_new_customer'] = (df['tenure'] <= 12).astype(int)
df['is_at_risk'] = ((df['total_charges'] / (df['monthly_charges'] + 1)) <= 24).astype(int)

print("\nNew Features Created:")
print(f"  1. avg_monthly_vs_total - Ratio of monthly to total charges")
print(f"     Correlation with churn: {df['avg_monthly_vs_total'].corr(df['churn']):.4f}")

print(f"\n  2. is_new_customer - Flag for tenure <= 12 months")
new_customer_churn = df[df['is_new_customer']==1]['churn'].mean() * 100
established_churn = df[df['is_new_customer']==0]['churn'].mean() * 100
print(f"     Churn rate (New): {new_customer_churn:.2f}%")
print(f"     Churn rate (Established): {established_churn:.2f}%")

print(f"\n  3. is_at_risk - Flag for short tenure relative to charges")
at_risk_churn = df[df['is_at_risk']==1]['churn'].mean() * 100
not_at_risk_churn = df[df['is_at_risk']==0]['churn'].mean() * 100
print(f"     Churn rate (At Risk): {at_risk_churn:.2f}%")
print(f"     Churn rate (Secure): {not_at_risk_churn:.2f}%")

# ======================== 13. SUMMARY STATISTICS TABLE ========================
print("\n13. KEY INSIGHTS SUMMARY")
print("-" * 80)

summary_stats = {
    'Metric': [
        'Total Customers',
        'Churned Customers',
        'Overall Churn Rate',
        'Avg Tenure (Retained)',
        'Avg Tenure (Churned)',
        'Avg Monthly Charge',
        'Median Total Charges',
        'Highest Churn Tenure Group',
        'Lowest Churn Tenure Group'
    ],
    'Value': [
        f"{len(df):,}",
        f"{df['churn'].sum():,}",
        f"{churn_rate:.2f}%",
        f"{df[df['churn']==0]['tenure'].mean():.1f} months",
        f"{df[df['churn']==1]['tenure'].mean():.1f} months",
        f"₹{df['monthly_charges'].mean():.2f}",
        f"₹{df['total_charges'].median():.2f}",
        "0-12 months",
        "48+ months"
    ]
}

summary_df = pd.DataFrame(summary_stats)
print(summary_df.to_string(index=False))

print("\n" + "=" * 80)
print("EDA COMPLETE!")
print("=" * 80)
print("\nVisualizations saved in: visualizations/ directory")
print("Ready for modeling!")
