# train_xgb_nopca.py
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Charger les données
df = pd.read_csv("balanced_backward.csv")

features = ["age", "cp", "thalach", "oldpeak", "ca", "thal"]
X = df[features]
y = df["target"].apply(lambda x: 1 if x > 0 else 0)  # Binaire

# Normalisation
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Séparation train/test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, stratify=y, random_state=42)

# Entraînement
dtrain = xgb.DMatrix(X_train, label=y_train)
model = xgb.train(params={
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "eta": 0.1,
    "max_depth": 3
}, dtrain=dtrain, num_boost_round=50)

# Sauvegarde
import os
os.makedirs("models", exist_ok=True)
model.save_model("models/xgb_nopca_model.json")

print("✅ Modèle sauvegardé dans models/xgb_nopca_model.json")
