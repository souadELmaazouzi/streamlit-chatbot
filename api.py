from flask import Flask, request, jsonify
import xgboost as xgb
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS

import re

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Questions attendues sans emoji
questions = [
    "Quel est votre âge ?",
    "Ressentez-vous des douleurs thoraciques ? (oui/non)",
    "Avez-vous des antécédents familiaux ? (oui/non)",
    "Votre fréquence cardiaque maximale mesurée ? (thalach)",
    "Niveau de dépression ST mesuré ? (oldpeak)",
    "Quel est votre type de thalassémie ? (1 = normal, 2 = fixe, 3 = réversible)"
]

# Correspondance des clés
feature_keys = ["age", "cp", "ca", "thalach", "oldpeak", "thal"]

# Fonction de nettoyage des questions (suppression emojis ou balises)
def strip_prefix(text):
    return re.sub(r"^(<.*?>|\W+)\s*", "", text).strip()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    history = data.get("history", [])

    if len(history) != len(questions) * 2:
        return jsonify({"reply": "❌ Mauvais format : 6 questions et 6 réponses attendues."}), 400

    answers = {}
    for i in range(0, len(history), 2):
        raw_q = history[i]
        raw_a = history[i + 1]
        clean_q = strip_prefix(raw_q)

        expected_q = questions[i // 2]
        if clean_q != expected_q:
            return jsonify({
                "reply": f"❌ Mauvaise question : attendu '{expected_q}', reçu '{clean_q}'"
            }), 400

        key = feature_keys[i // 2]
        try:
            if key in ["age", "thalach", "thal"]:
                value = int(raw_a)
            elif key == "oldpeak":
                value = float(raw_a)
            elif key in ["cp", "ca"]:
                value = 1 if raw_a.strip().lower() == "oui" else 0
            else:
                value = raw_a
            answers[key] = value
        except Exception as e:
            return jsonify({"reply": f"❌ Erreur de conversion pour '{key}': {str(e)}"}), 400

    # Prédiction
    try:
        df = pd.read_csv("balanced_backward.csv")
        scaler = MinMaxScaler()
        X = df[feature_keys]
        scaler.fit(X)

        input_df = pd.DataFrame([answers])
        scaled_input = scaler.transform(input_df)
        dmatrix = xgb.DMatrix(scaled_input, feature_names=feature_keys)

        model = xgb.Booster()
        model.load_model("models/xgb_nopca_model.json")

        prob = model.predict(dmatrix)[0]
        prediction = "⚠️ Risque élevé" if prob >= 0.25 else "✅ Faible risque"

        return jsonify({
            "reply": (
                f"🩺 Merci. Voici le résultat : {prediction}\n"
                f"🩺 Ceci est une évaluation automatique. Veuillez consulter un médecin.\n"
                f"🩺 Probabilité prédite : {prob:.2f}"
            )
        })

    except Exception as e:
        return jsonify({"reply": f"❌ Une erreur s'est produite côté serveur : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)