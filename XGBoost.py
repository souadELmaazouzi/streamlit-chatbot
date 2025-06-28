import os
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

# Paramètres XGBoost
params = {
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'eta': 0.1,
    'max_depth': 3,
    'lambda': 1,
    'alpha': 0
}
num_boost_round = 50

# Dossier contenant les fichiers PCA
pca_dir = "pca_results"
pca_files = [f for f in os.listdir(pca_dir) if f.endswith(".csv")]

# Liste pour stocker les résultats
results = []

# Traitement de chaque fichier PCA
for file in pca_files:
    df = pd.read_csv(os.path.join(pca_dir, file))

    # Séparation X/y
    X = df.drop(columns=["target"])
    y = df["target"]

    # Vérification : convertir y en binaire si nécessaire
    y = y.apply(lambda v: 1 if v > 0 else 0)

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Préparation pour XGBoost
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    # Entraînement
    model = xgb.train(params, dtrain, num_boost_round=num_boost_round)

    # Prédictions
    y_pred_prob = model.predict(dtest)
    y_pred = [1 if p >= 0.5 else 0 for p in y_pred_prob]

    # Évaluation
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)

    results.append({
        "PCA Source": file,
        "Accuracy": acc,
        "F1 Score": f1,
        "Recall": rec,
        "Precision": prec
    })

import pandas as pd

# Conversion en DataFrame
results_df = pd.DataFrame(results)

# Sauvegarde CSV
results_df.to_csv("xgboost_pca_summary.csv", index=False)

# Affichage en console
print(results_df)


# Sauvegarder le modèle
model.save_model("xgb_model.json")

# Création du dossier s’il n’existe pas
os.makedirs("models", exist_ok=True)

# Sauvegarder chaque modèle avec nom spécifique
model_name = file.replace(".csv", "_model.json")
model.save_model(os.path.join("models", model_name))