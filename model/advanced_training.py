"""
Advanced ML Model Training Pipeline for TelcoGuard
Includes: Model comparison, hyperparameter tuning, and comprehensive evaluation
"""

import pandas as pd
import numpy as np
import warnings
import json
from datetime import datetime
import pickle

# Machine Learning
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Imbalanced data handling
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Metrics
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve
)

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

print("=" * 100)
print("TELCGUARD: ADVANCED MACHINE LEARNING PIPELINE")
print("=" * 100)

# ======================== 1. DATA LOADING & PREPROCESSING ========================
print("\n1. LOADING AND PREPROCESSING DATA...")
print("-" * 100)

df = pd.read_csv("data/telco_churn.csv")
print(f"✓ Dataset loaded: {df.shape}")

# Handle missing values
df = df.dropna()
print(f"✓ Missing values handled: {df.shape}")

# Separate features and target
X = df.drop('churn', axis=1)
y = df['churn']

print(f"✓ Features: {X.shape[1]} | Target distribution: {y.value_counts().to_dict()}")

# ======================== 2. HANDLE CLASS IMBALANCE ========================
print("\n2. HANDLING CLASS IMBALANCE WITH SMOTE...")
print("-" * 100)

smote = SMOTE(random_state=42, k_neighbors=5)
X_balanced, y_balanced = smote.fit_resample(X, y)

print(f"✓ Original distribution: {pd.Series(y).value_counts().to_dict()}")
print(f"✓ Balanced distribution: {pd.Series(y_balanced).value_counts().to_dict()}")

# ======================== 3. TRAIN-TEST SPLIT ========================
print("\n3. SPLITTING DATA WITH STRATIFICATION...")
print("-" * 100)

X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced,
    test_size=0.2,
    random_state=42,
    stratify=y_balanced
)

print(f"✓ Training set: {X_train.shape}")
print(f"✓ Test set: {X_test.shape}")
print(f"✓ Training distribution: {pd.Series(y_train).value_counts().to_dict()}")

# ======================== 4. FEATURE SCALING ========================
print("\n4. FEATURE SCALING...")
print("-" * 100)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✓ Features scaled using StandardScaler")

# ======================== 5. MODEL DEFINITIONS ========================
print("\n5. DEFINING MACHINE LEARNING MODELS...")
print("-" * 100)

models = {
    'Logistic Regression': {
        'model': LogisticRegression(random_state=42, max_iter=1000),
        'params': {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],
            'solver': ['lbfgs', 'liblinear'],
            'penalty': ['l2']
        }
    },
    'Random Forest': {
        'model': RandomForestClassifier(random_state=42, n_jobs=-1),
        'params': {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    },
    'Gradient Boosting': {
        'model': GradientBoostingClassifier(random_state=42),
        'params': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5]
        }
    },
    'SVM': {
        'model': SVC(probability=True, random_state=42),
        'params': {
            'C': [0.1, 1, 10],
            'kernel': ['linear', 'rbf'],
            'gamma': ['scale', 'auto']
        }
    },
    'KNN': {
        'model': KNeighborsClassifier(),
        'params': {
            'n_neighbors': [3, 5, 7, 9],
            'weights': ['uniform', 'distance'],
            'metric': ['euclidean', 'manhattan']
        }
    }
}

print(f"✓ Defined {len(models)} models for comparison")
for model_name in models.keys():
    print(f"   - {model_name}")

# ======================== 6. HYPERPARAMETER TUNING & TRAINING ========================
print("\n6. HYPERPARAMETER TUNING (GridSearchCV)...")
print("-" * 100)

results = {}
trained_models = {}

for model_name, model_config in models.items():
    print(f"\n▶ Training {model_name}...")
    
    try:
        # GridSearchCV for hyperparameter tuning
        gs = GridSearchCV(
            model_config['model'],
            model_config['params'],
            cv=5,
            scoring='roc_auc',
            n_jobs=-1,
            verbose=0
        )
        
        gs.fit(X_train_scaled, y_train)
        best_model = gs.best_estimator_
        
        print(f"  ✓ Best parameters: {gs.best_params_}")
        print(f"  ✓ Best CV AUC score: {gs.best_score_:.4f}")
        
        # Predictions
        y_pred = best_model.predict(X_test_scaled)
        y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]
        
        # Evaluation metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc_roc = roc_auc_score(y_test, y_pred_proba)
        
        results[model_name] = {
            'model': best_model,
            'scaler': scaler,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc_roc': auc_roc,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'classification_report': classification_report(y_test, y_pred),
            'best_params': gs.best_params_
        }
        
        trained_models[model_name] = best_model
        
        print(f"  ✓ Accuracy:  {accuracy:.4f}")
        print(f"  ✓ Precision: {precision:.4f}")
        print(f"  ✓ Recall:    {recall:.4f}")
        print(f"  ✓ F1-Score:  {f1:.4f}")
        print(f"  ✓ AUC-ROC:   {auc_roc:.4f}")
        
    except Exception as e:
        print(f"  ✗ Error training {model_name}: {str(e)}")

# ======================== 7. MODEL COMPARISON ========================
print("\n7. MODEL COMPARISON")
print("-" * 100)

comparison_df = pd.DataFrame({
    'Model': list(results.keys()),
    'Accuracy': [results[m]['accuracy'] for m in results.keys()],
    'Precision': [results[m]['precision'] for m in results.keys()],
    'Recall': [results[m]['recall'] for m in results.keys()],
    'F1-Score': [results[m]['f1'] for m in results.keys()],
    'AUC-ROC': [results[m]['auc_roc'] for m in results.keys()]
}).sort_values('AUC-ROC', ascending=False)

print("\n" + comparison_df.to_string(index=False))

# ======================== 8. SELECT BEST MODEL ========================
print("\n8. MODEL SELECTION")
print("-" * 100)

best_model_name = comparison_df.iloc[0]['Model']
best_model = results[best_model_name]['model']
best_scaler = results[best_model_name]['scaler']

print(f"\n✓ Best Model: {best_model_name}")
print(f"  AUC-ROC Score: {results[best_model_name]['auc_roc']:.4f}")

# ======================== 9. FEATURE IMPORTANCE ========================
print("\n9. FEATURE IMPORTANCE ANALYSIS")
print("-" * 100)

if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Visualization
    plt.figure(figsize=(10, 8))
    sns.barplot(data=feature_importance.head(10), x='importance', y='feature', palette='viridis')
    plt.title(f'Top 10 Feature Importance - {best_model_name}', fontweight='bold', fontsize=14)
    plt.xlabel('Importance Score')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig('visualizations/06_feature_importance.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: visualizations/06_feature_importance.png")
    plt.close()

# ======================== 10. ROC CURVES ========================
print("\n10. GENERATING ROC CURVES...")
print("-" * 100)

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()
fig.suptitle('ROC Curves - Model Comparison', fontsize=16, fontweight='bold')

for idx, (model_name, model_results) in enumerate(results.items()):
    if idx >= len(axes):
        break
    
    fpr, tpr, _ = roc_curve(y_test, model_results['y_pred_proba'])
    roc_auc = auc(fpr, tpr)
    
    axes[idx].plot(fpr, tpr, color='darkorange', lw=2, 
                   label=f'ROC curve (AUC = {roc_auc:.4f})')
    axes[idx].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    axes[idx].set_xlabel('False Positive Rate')
    axes[idx].set_ylabel('True Positive Rate')
    axes[idx].set_title(model_name, fontweight='bold')
    axes[idx].legend(loc="lower right")
    axes[idx].grid(True, alpha=0.3)

# Hide unused subplots
for idx in range(len(results), len(axes)):
    axes[idx].axis('off')

plt.tight_layout()
plt.savefig('visualizations/07_roc_curves.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/07_roc_curves.png")
plt.close()

# ======================== 11. CONFUSION MATRICES ========================
print("\n11. GENERATING CONFUSION MATRICES...")
print("-" * 100)

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()
fig.suptitle('Confusion Matrices - Model Comparison', fontsize=16, fontweight='bold')

for idx, (model_name, model_results) in enumerate(results.items()):
    if idx >= len(axes):
        break
    
    cm = np.array(model_results['confusion_matrix'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'],
                cbar=False)
    axes[idx].set_title(model_name, fontweight='bold')
    axes[idx].set_ylabel('Actual')
    axes[idx].set_xlabel('Predicted')

for idx in range(len(results), len(axes)):
    axes[idx].axis('off')

plt.tight_layout()
plt.savefig('visualizations/08_confusion_matrices.png', dpi=300, bbox_inches='tight')
print("✓ Saved: visualizations/08_confusion_matrices.png")
plt.close()

# ======================== 12. CROSS-VALIDATION ========================
print("\n12. CROSS-VALIDATION ANALYSIS (5-Fold)...")
print("-" * 100)

cv_results = {}

for model_name in [best_model_name]:
    print(f"\nCross-validating {model_name}...")
    
    cv_scores = cross_validate(
        trained_models[model_name],
        X_train_scaled,
        y_train,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
        return_train_score=True,
        n_jobs=-1
    )
    
    cv_results[model_name] = cv_scores
    
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
        test_scores = cv_scores[f'test_{metric}']
        print(f"  {metric.upper()}:")
        print(f"    Mean: {test_scores.mean():.4f} (+/- {test_scores.std():.4f})")
        print(f"    Scores: {[f'{s:.4f}' for s in test_scores]}")

# ======================== 13. MODEL PERSISTENCE ========================
print("\n13. SAVING MODELS...")
print("-" * 100)

# Save best model
import joblib
joblib.dump(best_model, 'model/churn_model_best.pkl')
joblib.dump(best_scaler, 'model/scaler_best.pkl')
print(f"✓ Saved: model/churn_model_best.pkl")
print(f"✓ Saved: model/scaler_best.pkl")

# Save all results to JSON
results_summary = {
    'best_model': best_model_name,
    'timestamp': datetime.now().isoformat(),
    'comparison': comparison_df.to_dict('records'),
    'best_model_metrics': {
        'accuracy': float(results[best_model_name]['accuracy']),
        'precision': float(results[best_model_name]['precision']),
        'recall': float(results[best_model_name]['recall']),
        'f1': float(results[best_model_name]['f1']),
        'auc_roc': float(results[best_model_name]['auc_roc'])
    }
}

with open('model/training_results.json', 'w') as f:
    json.dump(results_summary, f, indent=4)

print(f"✓ Saved: model/training_results.json")

# ======================== 14. SUMMARY REPORT ========================
print("\n" + "=" * 100)
print("TRAINING SUMMARY REPORT")
print("=" * 100)

print(f"\n✓ Best Model: {best_model_name}")
print(f"✓ Models Tested: {len(results)}")
print(f"✓ Training Samples: {X_train.shape[0]} (after SMOTE balancing)")
print(f"✓ Test Samples: {X_test.shape[0]}")
print(f"✓ Features: {X.shape[1]}")
print(f"\nBest Model Performance:")
print(f"  • Accuracy:  {results[best_model_name]['accuracy']:.4f}")
print(f"  • Precision: {results[best_model_name]['precision']:.4f}")
print(f"  • Recall:    {results[best_model_name]['recall']:.4f}")
print(f"  • F1-Score:  {results[best_model_name]['f1']:.4f}")
print(f"  • AUC-ROC:   {results[best_model_name]['auc_roc']:.4f}")

print("\n" + "=" * 100)
print("PIPELINE COMPLETE!")
print("=" * 100)
