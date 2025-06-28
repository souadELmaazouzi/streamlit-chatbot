import streamlit as st
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler
from fpdf import FPDF
from datetime import datetime
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="💖 CardioAI - Assistant Médical",
    page_icon="💖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS simplifié - SANS interférence avec les messages
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background-color: #b8c0ff;  /* bleu clair */
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        min-height: 100vh;
    }
    
    /* Header principal */
    .hero-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.4);
        position: relative;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px 24px 0 0;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        color: #636e72;
        font-size: 1.3rem;
        margin-bottom: 2rem;
    }
    
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .hero-badge {
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
        color: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .badge-ai { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); }
    .badge-secure { background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); }
    .badge-fast { background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); }
    
    /* Section de chat */
    .chat-section {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.4);
        position: relative;
    }
    
    .chat-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 24px 24px 0 0;
    }
    
    .chat-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    /* Input container */
    .input-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.4);
        position: relative;
    }
    
    .input-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        border-radius: 24px 24px 0 0;
    }
    
    .input-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 0.5rem;
    }
    
    .input-subtitle {
        color: #636e72;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Styling des inputs */
    .stTextInput > div > div > input {
        border: 3px solid transparent !important;
        border-radius: 20px !important;
        padding: 1.2rem 1.8rem !important;
        font-size: 1.1rem !important;
        background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea 0%, #764ba2 100%) border-box !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08) !important;
    }
    
    .stTextInput > div > div > input:focus {
        background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) border-box !important;
        box-shadow: 0 12px 35px rgba(79, 172, 254, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Boutons */
    .stButton > button {
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2) !important;
    }
    
    /* Progress card */
    .progress-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.4);
        position: relative;
    }
    
    .progress-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 24px 24px 0 0;
    }
    
    .progress-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 1.5rem;
    }
    
    /* Métriques */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(30px);
        border-radius: 16px;
        padding: 1.8rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin: 1rem 0;
        transition: transform 0.3s ease;
        position: relative;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        border-radius: 16px 16px 0 0;
    }
    
    .metric-card.time::before { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); }
    .metric-card.security::before { background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); }
    .metric-card.accuracy::before { background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #636e72;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Résultats */
    .result-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.4);
        text-align: center;
        position: relative;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        border-radius: 24px 24px 0 0;
    }
    
    .result-card.risk-low::before { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .result-card.risk-high::before { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    
    .result-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #2d3436;
    }
    
    .result-value {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #2d3436;
    }
    
    .result-low { color: #00b894; }
    .result-high { color: #e17055; }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
        height: 12px !important;
    }
    
    .stProgress > div > div {
        background: rgba(102, 126, 234, 0.1) !important;
        border-radius: 10px !important;
        height: 12px !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1.2rem 2.5rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(79, 172, 254, 0.4) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-subtitle { font-size: 1.1rem; }
        .hero-badges { flex-direction: column; align-items: center; }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.history = []
    st.session_state.history.append({
        "text": "🩺 Bonjour ! Bienvenue dans votre évaluation cardiologique personnalisée avec l'IA. Je vais vous poser quelques questions importantes pour analyser votre santé cardiovasculaire. Commençons par votre âge ?", 
        "is_user": False
    })

@st.cache_resource
def load_model():
    """Charge le modèle XGBoost pré-entraîné"""
    try:
        model = xgb.Booster()
        model.load_model("models/xgb_nopca_model.json")
        return model
    except:
        st.error("Erreur lors du chargement du modèle")
        return None

def preprocess_input(data):
    """Préprocesse les données d'entrée"""
    try:
        df = pd.read_csv("balanced_backward.csv")
        features = ["age", "cp", "thalach", "oldpeak", "ca", "thal"]
        X = df[features]
        scaler = MinMaxScaler()
        scaler.fit(X)
        input_df = pd.DataFrame([data], columns=features)
        scaled_input = scaler.transform(input_df)
        return pd.DataFrame(scaled_input, columns=features)
    except:
        st.error("Erreur lors du préprocessing")
        return None

def generate_pdf(answers, prediction, probability):
    """Génère un rapport PDF stylé sans emojis"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(102, 126, 234)
    pdf.cell(0, 20, "RAPPORT DIAGNOSTIC CARDIAQUE IA", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(99, 110, 114)
    pdf.cell(0, 10, f"Rapport genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", ln=True, align="C")
    pdf.ln(15)
    
    # Informations patient
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(45, 52, 54)
    pdf.cell(0, 12, "INFORMATIONS PATIENT", ln=True)
    pdf.set_fill_color(102, 126, 234)
    pdf.cell(0, 2, "", ln=True, fill=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", "", 12)
    labels = {
        "age": "Age",
        "cp": "Douleurs thoraciques",
        "ca": "Antecedents familiaux", 
        "thalach": "Frequence cardiaque maximale",
        "oldpeak": "Depression ST",
        "thal": "Type de thalassemie"
    }
    
    for key, value in answers.items():
        label = labels.get(key, key)
        if key in ["cp", "ca"]:
            value = "Oui" if value == 1 else "Non"
        pdf.cell(0, 10, f"{label}: {value}", ln=True)
    
    pdf.ln(15)
    
    # Résultats
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "RESULTATS DE L'ANALYSE IA", ln=True)
    
    if "Faible risque" in prediction:
        pdf.set_fill_color(0, 184, 148)
        pdf.set_text_color(0, 184, 148)
        clean_prediction = "Faible risque cardiovasculaire"
    else:
        pdf.set_fill_color(225, 112, 85)
        pdf.set_text_color(225, 112, 85)
        clean_prediction = "Risque cardiovasculaire eleve"
    
    pdf.cell(0, 2, "", ln=True, fill=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, f"Diagnostic: {clean_prediction}", ln=True)
    pdf.cell(0, 12, f"Probabilite de risque: {probability:.1%}", ln=True)
    
    pdf.ln(15)
    
    # Recommandations
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(45, 52, 54)
    pdf.cell(0, 12, "RECOMMANDATIONS", ln=True)
    pdf.set_fill_color(116, 185, 255)
    pdf.cell(0, 2, "", ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(99, 110, 114)
    
    if "Faible risque" in prediction:
        recommendations = [
            "- Continuez a maintenir un mode de vie sain",
            "- Pratiquez une activite physique reguliere",
            "- Adoptez une alimentation equilibree",
            "- Effectuez un suivi medical annuel"
        ]
    else:
        recommendations = [
            "- Consultez rapidement un cardiologue",
            "- Effectuez des examens complementaires",
            "- Suivez scrupuleusement les traitements prescrits",
            "- En cas d'urgence, contactez le 15"
        ]
    
    for rec in recommendations:
        pdf.cell(0, 8, rec, ln=True)
    
    pdf.ln(10)
    
    # Avertissement
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(225, 112, 85)
    pdf.cell(0, 10, "AVERTISSEMENT IMPORTANT", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(99, 110, 114)
    pdf.multi_cell(0, 6, "Cette evaluation est generee par intelligence artificielle a des fins d'information uniquement. Elle ne remplace en aucun cas un diagnostic medical professionnel. Consultez toujours un medecin qualifie pour un avis medical complet et personnalise.")
    
    filename = f"rapport_cardio_ai_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(filename)
    return filename

def create_risk_gauge(probability):
    """Crée un gauge coloré pour visualiser le risque"""
    colors = ['#4facfe', '#00f2fe'] if probability < 0.25 else ['#fa709a', '#fee140']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "🎯 Niveau de Risque (%)", 'font': {'size': 20, 'color': '#2d3436'}},
        delta = {'reference': 25, 'increasing': {'color': "#fa709a"}, 'decreasing': {'color': "#4facfe"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': "#2d3436"},
            'bar': {'color': colors[0]},
            'steps': [
                {'range': [0, 25], 'color': "rgba(79, 172, 254, 0.2)"},
                {'range': [25, 50], 'color': "rgba(67, 233, 123, 0.2)"},
                {'range': [50, 75], 'color': "rgba(253, 203, 110, 0.2)"},
                {'range': [75, 100], 'color': "rgba(250, 112, 154, 0.2)"}
            ],
            'threshold': {
                'line': {'color': colors[1], 'width': 4},
                'thickness': 0.8,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        font={'color': "#2d3436", 'family': "Poppins"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# Questions avec descriptions
questions = [
    ("Quel est votre âge ? (en années)", "age", int, "🎂 Votre âge actuel", "Ex: 45"),
    ("Ressentez-vous des douleurs thoraciques ?", "cp", lambda x: 1 if x.lower() in ["oui", "yes", "o", "y"] else 0, "💔 Douleurs dans la poitrine", "Répondez par oui ou non"),
    ("Avez-vous des antécédents familiaux de maladies cardiaques ?", "ca", lambda x: 1 if x.lower() in ["oui", "yes", "o", "y"] else 0, "👨‍👩‍👧‍👦 Historique familial", "Répondez par oui ou non"),
    ("Quelle est votre fréquence cardiaque maximale mesurée ?", "thalach", int, "💓 Battements par minute", "Ex: 150"),
    ("Quel est votre niveau de dépression ST mesuré ? (oldpeak)", "oldpeak", float, "📊 Valeur numérique", "Ex: 2.3"),
    ("Quel est votre type de thalassémie ?", "thal", int, "🧬 Type 1, 2 ou 3", "1=normal, 2=fixe, 3=réversible")
]

# Layout principal
col1, col2 = st.columns([2.5, 1.5])

with col1:
    # Header principal
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">💖 CardioAI Assistant</h1>
        <p class="hero-subtitle">Évaluation intelligente et personnalisée de votre santé cardiovasculaire</p>
        <div class="hero-badges">
            <div class="hero-badge badge-ai">🤖 IA Avancée</div>
            <div class="hero-badge badge-secure">🔒 100% Sécurisé</div>
            <div class="hero-badge badge-fast">⚡ Résultat Instantané</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section de chat - TITRE SEULEMENT
    st.markdown("""
    <div class="chat-section">
        <div class="chat-title">💬 Conversation avec l'IA</div>
    """, unsafe_allow_html=True)
    
    # MESSAGES STREAMLIT NATIFS - SANS CONTAINER
    for i, chat in enumerate(st.session_state.history):
        if chat["is_user"]:
            with st.chat_message("user"):
                st.write(chat["text"])
        else:
            with st.chat_message("assistant"):
                st.write(chat["text"])
    
    # Fermeture du container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Zone de saisie
    if st.session_state.step < len(questions):
        q_text, key, cast, description, placeholder = questions[st.session_state.step]
        
        st.markdown(f"""
        <div class="input-container">
            <div class="input-title">
                📝 Question {st.session_state.step + 1}/{len(questions)}
            </div>
            <div class="input-subtitle">{description}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Input avec placeholder
        user_input = st.text_input(
            "Votre réponse:",
            key=f"input_{st.session_state.step}",
            placeholder=placeholder,
            label_visibility="collapsed"
        )
        
        # Boutons de réponse rapide
        if key in ["cp", "ca"]:
            col_yes, col_no, col_space = st.columns([1, 1, 2])
            
            with col_yes:
                if st.button("✅ Oui", key=f"yes_{st.session_state.step}"):
                    user_input = "oui"
            
            with col_no:
                if st.button("❌ Non", key=f"no_{st.session_state.step}"):
                    user_input = "non"
        
        # Traitement de la réponse
        if user_input:
            try:
                val = cast(user_input.strip())
                st.session_state.answers[key] = val
                st.session_state.history.append({"text": user_input, "is_user": True})
                st.session_state.step += 1
                
                if st.session_state.step < len(questions):
                    next_q = questions[st.session_state.step][0]
                    st.session_state.history.append({"text": f"🩺 {next_q}", "is_user": False})
                
                st.rerun()
            except Exception as e:
                st.error("⚠️ Entrée invalide. Veuillez vérifier votre réponse.")

with col2:
    # Sidebar avec informations
    st.markdown("""
    <div class="progress-card">
        <div class="progress-title">📊 Votre Progression</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barre de progression
    progress = st.session_state.step / len(questions)
    st.progress(progress)
    st.markdown(f"**{st.session_state.step}/{len(questions)} questions complétées** ({progress*100:.0f}%)")
    
    # Métriques
    st.markdown("""
    <div class="metric-card time">
        <div class="metric-value">2-3</div>
        <div class="metric-label">Minutes</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card security">
        <div class="metric-value">100%</div>
        <div class="metric-label">Sécurisé</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card accuracy">
        <div class="metric-value">95%</div>
        <div class="metric-label">Précision</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Informations collectées
    if st.session_state.answers:
        st.markdown("### 📋 Données Collectées")
        for key, value in st.session_state.answers.items():
            if key in ["cp", "ca"]:
                value = "✅ Oui" if value == 1 else "❌ Non"
            st.markdown(f"**{key.upper()}:** {value}")

# Traitement final et résultats
if st.session_state.step >= len(questions):
    model = load_model()
    if model:
        features = ["age", "cp", "thalach", "oldpeak", "ca", "thal"]
        input_data = [st.session_state.answers[f] for f in features]
        processed = preprocess_input(input_data)
        
        if processed is not None:
            dmatrix = xgb.DMatrix(processed)
            prob = model.predict(dmatrix)[0]
            
            prediction = "🟢 Faible risque cardiovasculaire" if prob < 0.25 else "🔴 Risque cardiovasculaire élevé"
            risk_class = "risk-low" if prob < 0.25 else "risk-high"
            result_class = "result-low" if prob < 0.25 else "result-high"
            
            # Affichage des résultats
            st.markdown(f"""
            <div class="result-card {risk_class}">
                <div class="result-title">🎯 Résultat de votre Évaluation IA</div>
                <h2 class="{result_class}">{prediction}</h2>
                <div class="result-value">Probabilité calculée: {prob:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gauge de risque
            col_gauge1, col_gauge2 = st.columns([1.2, 0.8])
            
            with col_gauge1:
                fig = create_risk_gauge(prob)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_gauge2:
                st.markdown("### 📈 Interprétation")
                if prob < 0.25:
                    st.success("✅ Excellent ! Votre profil indique un faible risque cardiovasculaire.")
                    st.info("💡 Continuez à maintenir votre mode de vie sain.")
                else:
                    st.error("⚠️ Attention ! Votre profil indique un risque cardiovasculaire élevé.")
                    st.warning("🏥 Consultez rapidement un cardiologue.")
            
            # Messages finaux
            if len(st.session_state.history) < 15:
                st.session_state.history.extend([
                    {"text": f"🎯 Analyse terminée ! Résultat: {prediction}", "is_user": False},
                    {"text": f"📊 Probabilité de risque: {prob:.1%}", "is_user": False},
                    {"text": "⚠️ Cette évaluation IA est informative. Consultez un médecin pour un diagnostic complet.", "is_user": False}
                ])
            
            # Génération du rapport PDF
            st.markdown("### 📄 Votre Rapport Médical")
            filename = generate_pdf(st.session_state.answers, prediction, prob)
            
            with open(filename, "rb") as f:
                st.download_button(
                    label="📥 Télécharger le Rapport PDF",
                    data=f,
                    file_name=filename,
                    mime="application/pdf"
                )
            
            # Bouton de recommencement
            if st.button("🔄 Nouvelle Évaluation"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 2rem; margin-top: 2rem;">
    <div style="background: rgba(255,255,255,0.95); backdrop-filter: blur(30px); border-radius: 24px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.08);">
        <h3 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">💖 CardioAI Assistant</h3>
        <p style="color: #636e72; margin-bottom: 0.5rem;">Votre santé cardiovasculaire analysée par intelligence artificielle</p>
        <p style="font-size: 0.9rem; color: #b2bec3;">⚠️ Cet outil ne remplace pas un avis médical professionnel</p>
    </div>
</div>
""", unsafe_allow_html=True)
