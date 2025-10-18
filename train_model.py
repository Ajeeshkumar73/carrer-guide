#!/usr/bin/env python3
"""
train_model.py (default-friendly)

You can run:
  python train_model.py
or:
  python train_model.py --csv myfile.csv --target my_target
"""
import argparse
import sys
import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def parse_args():
    p = argparse.ArgumentParser(description="Train and save a career prediction pipeline.")
    p.add_argument("--csv", "-c", default="career_synthetic.csv", help="Path to training CSV file. (default: career_synthetic.csv)")
    p.add_argument("--target", "-t", default=None, help="Name of the target column. If omitted, common names will be checked.")
    p.add_argument("--out", "-o", default="career_rf_model.pkl", help="Output pipeline path.")
    p.add_argument("--pre", "-p", default="career_preprocessor.pkl", help="Output preprocessor path (optional).")
    return p.parse_args()

def find_target_column(df, provided=None):
    if provided and provided in df.columns:
        return provided
    candidates = ["career_domain", "career_label", "career", "target", "label"]
    for c in candidates:
        if c in df.columns:
            print(f"[info] Found likely target column: '{c}'")
            return c
    return None

def safe_create_numeric(df):
    if "problem_solving" in df.columns and "problem_solving_num" not in df.columns:
        df["problem_solving_num"] = df["problem_solving"].map({"high":2,"medium":1,"low":0}).fillna(1).astype(int)
    if "creativity" in df.columns and "creativity_num" not in df.columns:
        df["creativity_num"] = df["creativity"].map({"high":2,"medium":1,"low":0}).fillna(1).astype(int)
    if "data_interest" in df.columns and "data_interest_num" not in df.columns:
        df["data_interest_num"] = df["data_interest"].map({"high":2,"low":0}).fillna(0).astype(int)
    if "communication" in df.columns and "communication_num" not in df.columns:
        df["communication_num"] = df["communication"].map({"high":2,"medium":1,"low":0}).fillna(1).astype(int)
    if "entrepreneurial_pref" in df.columns and "entrepreneurial_num" not in df.columns:
        df["entrepreneurial_num"] = df["entrepreneurial_pref"].map({"high":2,"low":0}).fillna(0).astype(int)
    if "coding_interest" in df.columns and "coding_interest_bin" not in df.columns:
        df["coding_interest_bin"] = df["coding_interest"].map({"yes":1,"no":0}).fillna(0).astype(int)
    if "long_study" in df.columns and "long_study_bin" not in df.columns:
        df["long_study_bin"] = df["long_study"].map({"yes":1,"no":0}).fillna(0).astype(int)

def main():
    args = parse_args()
    csv_path = args.csv
    if not os.path.exists(csv_path):
        print(f"[error] CSV file not found: {csv_path}")
        sys.exit(1)

    print(f"[info] Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[info] CSV loaded — shape: {df.shape}")
    print("[info] Columns detected in CSV:")
    for col in df.columns:
        print("  -", col)

    target_col = find_target_column(df, provided=args.target)
    if target_col is None:
        print("\n[error] Could not find the target column automatically.")
        print("Please specify the target column name using --target, or rename the correct column to one of:")
        print("  career_domain, career_label, career, target, label")
        print("\nAvailable columns are:")
        for col in df.columns:
            print("  -", col)
        sys.exit(2)

    print(f"[info] Using target column: '{target_col}'\n")
    if target_col not in df.columns:
        print(f"[error] Provided target column '{target_col}' not found in CSV.")
        sys.exit(3)

    safe_create_numeric(df)

    num_cols = [c for c in ["problem_solving_num", "creativity_num", "data_interest_num", "communication_num", "entrepreneurial_num"] if c in df.columns]
    cat_cols = [c for c in ["fav_subject", "hands_on_pref", "coding_interest_bin", "long_study_bin", "work_env"] if c in df.columns]

    if not num_cols and not cat_cols:
        print("[warn] No known numeric/categorical feature names found. Will try using all columns except target.")
        features = [c for c in df.columns if c != target_col]
    else:
        features = num_cols + cat_cols

    print(f"[info] Feature columns to be used ({len(features)}): {features}")

    X = df[features]
    y = df[target_col]

    if X.shape[0] < 10:
        print("[warn] Very few rows in CSV (<10). Model training may fail or overfit.")
    if y.nunique() < 2:
        print("[error] Target column appears to have less than 2 classes — cannot train a classifier.")
        sys.exit(4)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    num_transform = ("num", StandardScaler(), num_cols) if num_cols else ("num", "passthrough", [])
    cat_transform = ("cat",OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols) if cat_cols else ("cat", "passthrough", [])
    preprocessor = ColumnTransformer(transformers=[num_transform, cat_transform], remainder="drop")

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    pipe = Pipeline([("pre", preprocessor), ("clf", clf)])
    print("[info] Training pipeline ...")
    pipe.fit(X_train, y_train)

    print("[info] Training complete. Evaluating on test set ...")
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[info] Test accuracy: {acc:.4f}")
    print("[info] Classification report:\n")
    print(classification_report(y_test, y_pred))

    out_path = args.out
    pre_out = args.pre
    joblib.dump(pipe, out_path)
    joblib.dump(preprocessor, pre_out)
    print(f"[info] Saved pipeline to: {out_path}")
    print(f"[info] Saved preprocessor to: {pre_out}")

    try:
        print("\n[info] Pipeline.feature_names_in_ (if available):")
        print(getattr(pipe, "feature_names_in_", "N/A"))
    except Exception:
        pass

    print("\n[done] You can now copy the pipeline file to your Django BASE_DIR and run the server.")

if __name__ == "__main__":
    main()
