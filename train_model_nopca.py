# train_model_nopca.py
import pandas as pd
import xgboost as xgb
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("balanced_backward.csv")
features = ["age", "cp", "ca", "thalach", "oldpeak", "thal"]

X = df[features]
y = df["target"]

# Normalisation
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Entraînement XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=features)
dtest = xgb.DMatrix(X_test, label=y_test, feature_names=features)

params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss"
}

model = xgb.train(params, dtrain, num_boost_round=100)

# Sauvegarde du modèle et du scaler
os.makedirs("models", exist_ok=True)
model.save_model("models/xgb_nopca_model.json")
joblib.dump(scaler, "models/scaler_nopca.pkl")

print("✅ Modèle et scaler enregistrés dans le dossier models/")
