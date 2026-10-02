"""
ApplyCM ML Model Training and Evaluation Pipeline.
Trains a RandomForestClassifier with baseline comparison against LogisticRegression.
Computes evaluation metrics (Accuracy, Top-3 Accuracy, Confusion Matrix, Feature Importance)
and saves slide-ready plots and serialized model bundle.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib

# Ensure matplotlib runs in headless mode
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, top_k_accuracy_score, confusion_matrix, classification_report

from app.ml.field_mapping import TARGET_FIELDS
from app.ml.generate_dataset import (
    QUESTION_KEYS,
    SERIES_OPTIONS,
    SUBJECT_OPTIONS,
    generate_dataset,
)


from typing import Tuple, List, Dict, Any


def build_feature_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """
    Transforms dataframe rows into numeric feature vectors:
    - 12 interest scores (1-5)
    - One-hot binary columns for series
    - Multi-hot binary columns for subjects
    """
    # 1. 12 Question columns
    feature_dfs = [df[QUESTION_KEYS].copy()]

    # 2. One-hot for academic series
    series_encoded = pd.get_dummies(df["series"], prefix="series")
    # Ensure all series options exist
    for s in SERIES_OPTIONS:
        col = f"series_{s}"
        if col not in series_encoded.columns:
            series_encoded[col] = 0
    feature_dfs.append(series_encoded)

    # 3. Multi-hot for subjects
    subject_cols = {}
    for subj in SUBJECT_OPTIONS:
        col_name = f"subj_{subj.lower().replace(' ', '_')}"
        # A student has this subject if it's in subject_1, subject_2, or subject_3
        has_subj = (
            (df["subject_1"] == subj)
            | (df["subject_2"] == subj)
            | (df["subject_3"] == subj)
        ).astype(int)
        subject_cols[col_name] = has_subj
    subject_df = pd.DataFrame(subject_cols, index=df.index)
    feature_dfs.append(subject_df)

    X = pd.concat(feature_dfs, axis=1)
    feature_names = X.columns.tolist()
    return X, feature_names


def transform_single_student(answers: dict, feature_names: list) -> np.ndarray:
    """
    Transforms single questionnaire answer dictionary into a 2D numpy array
    aligned with the training feature_names.
    """
    row = {}
    # 1. 12 Questions
    for q in QUESTION_KEYS:
        row[q] = float(answers.get(q, 3))

    # 2. Series
    student_series = answers.get("series", "Science")
    for s in SERIES_OPTIONS:
        row[f"series_{s}"] = 1.0 if student_series == s else 0.0

    # 3. Subjects
    student_subjects = answers.get("subjects", [])
    for subj in SUBJECT_OPTIONS:
        col_name = f"subj_{subj.lower().replace(' ', '_')}"
        row[col_name] = 1.0 if subj in student_subjects else 0.0

    # Align with training features
    vector = [row.get(col, 0.0) for col in feature_names]
    return pd.DataFrame([vector], columns=feature_names)


def train_and_evaluate(data_path: str = None, models_dir: str = None):
    """
    Complete training pipeline:
    1. Loads or generates dataset
    2. Trains Logistic Regression baseline
    3. Trains Random Forest Classifier
    4. Computes Accuracy & Top-3 Accuracy
    5. Saves confusion matrix and feature importance PNG plots
    6. Saves trained joblib artifact
    """
    if models_dir is None:
        models_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    os.makedirs(models_dir, exist_ok=True)

    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "data", "student_dataset.csv")

    if not os.path.exists(data_path):
        print("Dataset not found. Generating 3,200 synthetic student profiles...")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df = generate_dataset(num_per_field=400, noise_ratio=0.12)
        df.to_csv(data_path, index=False)
    else:
        print(f"Loading dataset from: {data_path}")
        df = pd.read_csv(data_path)

    print(f"Total samples: {len(df)}")
    X, feature_names = build_feature_matrix(df)
    y = df["target_field"]

    # 80/20 Train/Test Split (Stratified to maintain class balance)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("\n" + "=" * 60)
    print("STAGE 1: TRAINING BASELINE MODEL (Logistic Regression)")
    print("=" * 60)
    baseline_clf = LogisticRegression(max_iter=1000, random_state=42)
    baseline_clf.fit(X_train, y_train)

    base_preds = baseline_clf.predict(X_test)
    base_probs = baseline_clf.predict_proba(X_test)
    base_acc = accuracy_score(y_test, base_preds)
    base_top3_acc = top_k_accuracy_score(y_test, base_probs, k=3, labels=baseline_clf.classes_)

    print(f"Baseline (Logistic Regression) Test Accuracy:       {base_acc * 100:.2f}%")
    print(f"Baseline (Logistic Regression) Top-3 Accuracy:     {base_top3_acc * 100:.2f}%")

    print("\n" + "=" * 60)
    print("STAGE 2: TRAINING MAIN MODEL (Random Forest Classifier)")
    print("=" * 60)
    rf_clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=14,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    rf_clf.fit(X_train, y_train)

    rf_preds = rf_clf.predict(X_test)
    rf_probs = rf_clf.predict_proba(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_top3_acc = top_k_accuracy_score(y_test, rf_probs, k=3, labels=rf_clf.classes_)

    # 5-Fold Cross Validation
    cv_scores = cross_val_score(rf_clf, X, y, cv=5, scoring="accuracy")

    print(f"Random Forest Test Accuracy:                      {rf_acc * 100:.2f}%")
    print(f"Random Forest Top-3 Accuracy:                     {rf_top3_acc * 100:.2f}%")
    print(f"Random Forest 5-Fold CV Accuracy:                 {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")
    print(f"Accuracy Gain over Baseline:                      +{(rf_acc - base_acc) * 100:.2f}%")

    print("\nClassification Report (Random Forest):")
    print(classification_report(y_test, rf_preds, digits=3))

    # =========================================================================
    # PLOT 1: Confusion Matrix for Slide Presentations
    # =========================================================================
    cm = confusion_matrix(y_test, rf_preds, labels=rf_clf.classes_)
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(cm, cmap="Blues")
    fig.colorbar(cax)

    ax.set_xticks(range(len(rf_clf.classes_)))
    ax.set_yticks(range(len(rf_clf.classes_)))
    ax.set_xticklabels(rf_clf.classes_, rotation=45, ha="left", fontsize=9)
    ax.set_yticklabels(rf_clf.classes_, fontsize=9)
    ax.set_xlabel("Predicted Field of Study", fontweight="bold")
    ax.set_ylabel("True Field of Study", fontweight="bold")
    ax.set_title("ApplyCM AI: Confusion Matrix (Test Set)", fontsize=13, fontweight="bold", pad=20)

    for i in range(len(rf_clf.classes_)):
        for j in range(len(rf_clf.classes_)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black" if cm[i, j] < cm.max()/2 else "white")

    plt.tight_layout()
    cm_path = os.path.join(models_dir, "confusion_matrix.png")
    fig.savefig(cm_path, dpi=200)
    plt.close(fig)
    print(f"Confusion Matrix saved to: {cm_path}")

    # =========================================================================
    # PLOT 2: Feature Importance for Slide Presentations
    # =========================================================================
    importances = rf_clf.feature_importances_
    top_indices = np.argsort(importances)[::-1][:15]  # Top 15 features
    top_features = [feature_names[i] for i in top_indices]
    top_scores = importances[top_indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(top_features)), top_scores[::-1], color="#2563EB")
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features[::-1], fontsize=9)
    ax.set_xlabel("Relative Feature Importance (Gini Impurity Decrease)", fontweight="bold")
    ax.set_title("Top 15 Most Predictive Questions & Features", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fi_path = os.path.join(models_dir, "feature_importance.png")
    fig.savefig(fi_path, dpi=200)
    plt.close(fig)
    print(f"Feature Importance plot saved to: {fi_path}")

    # =========================================================================
    # SAVE SERIALIZED ARTIFACT
    # =========================================================================
    bundle = {
        "model": rf_clf,
        "classes": rf_clf.classes_.tolist(),
        "feature_names": feature_names,
        "series_options": SERIES_OPTIONS,
        "subject_options": SUBJECT_OPTIONS,
        "question_keys": QUESTION_KEYS,
        "metrics": {
            "rf_accuracy": float(rf_acc),
            "rf_top3_accuracy": float(rf_top3_acc),
            "baseline_accuracy": float(base_acc),
            "baseline_top3_accuracy": float(base_top3_acc),
            "cv_accuracy_mean": float(cv_scores.mean()),
            "cv_accuracy_std": float(cv_scores.std()),
        },
    }

    model_bundle_path = os.path.join(models_dir, "career_model.joblib")
    joblib.dump(bundle, model_bundle_path)
    print(f"Trained model bundle successfully saved to: {model_bundle_path}")

    return bundle


if __name__ == "__main__":
    train_and_evaluate()
