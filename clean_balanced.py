import pandas as pd
import numpy as np

# Charger le fichier d'origine avec header explicite
df = pd.read_csv("merged_heart_data.csv", header=None)

# Affecter les noms de colonnes
df.columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
              "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target", "source"]

# Nettoyage : remplacer '?' par NaN
df.replace('?', np.nan, inplace=True)

# Conversion en numérique
for col in ["ca", "thal", "oldpeak", "thalach", "age"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Supprimer les lignes avec des NaN
df.dropna(inplace=True)

# Colonnes sélectionnées par Backward
selected_cols = ["age", "cp", "thalach", "oldpeak", "ca", "thal"]

# Créer le fichier nettoyé
balanced_df = df[selected_cols + ["target"]]
balanced_df.to_csv("balanced_backward.csv", index=False)

print("✅ Fichier 'balanced_backward.csv' nettoyé et sauvegardé avec succès.")
