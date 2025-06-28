import pandas as pd

# Charger le dataset complet nettoyé
df = pd.read_csv("merged_heart_data.csv", header=None)

# Assigner noms des colonnes
df.columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
              "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target", "source"]

# Garder uniquement les colonnes sélectionnées par Backward + target
selected_cols = ["age", "cp", "thalach", "oldpeak", "ca", "thal"]
balanced_df = df[selected_cols + ["target"]]

# Sauvegarder dans un fichier CSV
balanced_df.to_csv("balanced_backward.csv", index=False)

print("✅ Fichier 'balanced_backward.csv' créé avec succès.")
