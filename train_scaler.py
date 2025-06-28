import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Charger les données
df = pd.read_csv("balanced_backward.csv")

# Colonnes utilisées dans l'API et le modèle
features = ["age", "cp", "ca", "thalach", "oldpeak", "thal"]

# Vérification
if not all(col in df.columns for col in features):
    missing = [col for col in features if col not in df.columns]
    raise ValueError(f"Les colonnes suivantes sont manquantes dans le CSV : {missing}")

# Entraîner le scaler
scaler = MinMaxScaler()
scaler.fit(df[features])

# Sauvegarder le scaler
os.makedirs("models", exist_ok=True)
joblib.dump(scaler, "models/scaler_nopca.pkl")

print("✅ Scaler sauvegardé dans models/scaler_nopca.pkl")
