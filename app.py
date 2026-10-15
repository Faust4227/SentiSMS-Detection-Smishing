import streamlit as st
import pandas as pd
import re
from sklearn.ensemble import RandomForestClassifier
from build_url_dataset import extract_24_features

# 1. Configuration de la page
st.set_page_config(
    page_title="SentiSMS — Sécurité & Détection Smishing",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling CSS Chic & Haute Lisibilité (Fond Beige #FAF7F0 sans toucher au champ de texte d'origine)
st.markdown("""
    <style>

    /* ========================================================= */
    /* BARRE DE NAVIGATION HORIZONTALE                           */
    /* ========================================================= */
    .horizontal-nav {
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 16px;
        padding: 1rem 1.8rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }

    .nav-item-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #f43f5e;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .nav-item-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.9rem;
        color: #ffffff;
        font-weight: 500;
    }

    /* Style personnalisé pour l'image du Hero Banner */
    .custom-hero-img {
    width: 100%;             
    height: 400px;           
    object-fit: cover;       
    border-radius: 20px;     
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4); 
    border: 1px solid rgba(244, 63, 94, 0.3);   
    }
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Style global de l'application (Background Beige #FAF7F0 & textes lisibles) */
    .stApp {
        background: #FAF7F0 !important;
        color: #0f172a !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* Conteneur principal Hero */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(244, 63, 94, 0.3);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }

    /* Titres avec dégradé chic */
    .hero-brand {
        font-family: 'Outfit', sans-serif;
        font-size: 6.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 40%, #fb7185 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        line-height: 1.1;
    }

    .hero-slogan {
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 400;
        color: #e2e8f0;
        margin-bottom: 1rem;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(244, 63, 94, 0.2);
        color: #fda4af;
        border: 1px solid rgba(244, 63, 94, 0.4);
        padding: 0.4rem 1.1rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 1.2rem;
    }

    /* Cartes d'information au contraste très élevé */
    .senticard {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }

    .senticard h5 {
        color: #f43f5e;
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .senticard p, .senticard li {
        color: #e2e8f0 !important;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Barre latérale Sidebar */
    [data-testid="stSidebar"] {
        background-color: #060911;
        border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* ========================================================= */
    /* PERSONNALISATION DES COULEURS DES RÉSULTATS (DIAGNOSTIC)  */
    /* ========================================================= */

    .stAlert[data-baseweb="notification"] {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    div[data-testid="stNotificationContentError"] {
        color: #ff4d4d !important; 
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stNotificationContentWarning"] {
        color: #cc9900 !important; 
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stNotificationContentSuccess"] {
        color: #00b050 !important; 
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* Onglets styling */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%) !important;
        border: 1px solid rgba(244, 2, 1, 0.3) !important;
        border-radius: 16px !important;
        padding: 8px 12px !important;
        gap: 8px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4) !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important; 
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [data-baseweb="tab"] p, 
    .stTabs [data-baseweb="tab"] span {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important; 
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }

    .stTabs [aria-selected="true"] {
        background: #172033 !important; 
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.4) !important;
    }

    .stTabs [aria-selected="true"] p, 
    .stTabs [aria-selected="true"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Mots-clés suspects dans le texte
SMS_SUSPICIOUS_KEYWORDS = [
    'urgent', 'bloque', 'suspension', 'securite', 'momo', 'mobile money', 'compte',
    'gagne', 'gagnant', 'felicitations', 'loterie', 'code', 'pin', 'otp', 'verification',
    'mettre a jour', 'recharge', 'banque', 'virement', 'colis', 'livraison', 'limité',
    'impot', 'pass', 'password', 'service', 'free', 'gift',
    'winner', 'gagner', 'mobilemoney', 'momo', 'orange', 'moov', 'mtn', '24 h', 'vite',
    'bloqué', 'suspendu', 'alerte de sécurité', 'Blocked', 'mise à jour obligatoire',
    'immédiatement', 'dernier avis', 'PIN', 'Security alert', 'Refund', 'Payment', 'Prize', 'Free',
    'au plus vite', 'Immediately', 'confirm', 'validate', 'click here', 'act now', 'update now',
    'remboursement', 'paiement', 'transaction', 'gratuit', 'cadeau', 'valider', 'confirmer',
    'gagnant', 'mot de passe', 'mettez à jour maintenant', 'cliquez ici', 'verrouillé', 'urgent'
]


def extract_urls_from_text(text):
    url_pattern = r'https?://[^\s]+|www\.[^\s]+'
    return re.findall(url_pattern, text)


def analyze_sms_text(text):
    text_lower = text.lower()
    found_keywords = [kw for kw in SMS_SUSPICIOUS_KEYWORDS if kw in text_lower]
    text_score = min(len(found_keywords) * 25, 100)
    return text_score, found_keywords


# 4. Chargement du modèle Machine Learning
@st.cache_resource
def load_trained_model():
    df_train = pd.read_csv('url_dataset/train.csv')
    X_train = df_train.drop(columns=['url', 'label'])
    y_train = df_train['label']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, len(df_train)


model, train_size = load_trained_model()

# 5. Barre d'information Horizontale (Navigation / Fiche Technique)
st.markdown("<div class='horizontal-nav'>", unsafe_allow_html=True)
c_logo, c_info1, c_info2, c_info3 = st.columns([1, 2, 2, 2])

with c_logo:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://img.icons8.com/color/96/000000/shield.png" width="45">
            <div>
                <div style="font-family: Outfit; font-weight: 800; font-size: 1.4rem; color: #ffffff;">SentiSMS</div>
                <div style="font-size: 0.75rem; color: #fda4af; font-weight: 600;">Sentinelle IA</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c_info1:
    st.markdown("""
        <div class="nav-item-title">⚙️ Moteur IA</div>
        <div class="nav-item-value">Random Forest Classifier (100 Arbres)</div>
    """, unsafe_allow_html=True)

with c_info2:
    st.markdown("""
        <div class="nav-item-title">🔍 Analyse Hybride</div>
        <div class="nav-item-value">Sémantique SMS + 24 Features URL</div>
    """, unsafe_allow_html=True)

with c_info3:
    st.markdown("""
        <div class="nav-item-title">🇧🇯 Périmètre National</div>
        <div class="nav-item-value">Protection Mobile Money & Banques Bénin</div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 6. BANDEAU D'EN-TÊTE D'IMPACT (HERO SECTION)
col_hero_img, col_hero_text = st.columns([1, 2], gap="large")

with col_hero_img:
    st.markdown("""
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLK67llP5ZaTqKh4-qWjeQWgGf5Ozz4q-UlsunW9P1Ig&s=10" class="custom-hero-img" alt="Illustration SentiSMS">
    """, unsafe_allow_html=True)

with col_hero_text:
    st.markdown("""
        <div class="hero-container">
            <span class="hero-badge">🛡️ PLATEFORME NATIONALE CYBER & IA</span>
            <div class="hero-brand">SentiSMS</div>
            <div class="hero-slogan">« Un SMS suspect ? Vérifiez avant d'agir. »</div>
            <p style="color: #cbd5e1; margin-top: 1rem; font-size: 1.05rem; line-height: 1.6;">
                Analysez vos messages instantanément. SentiSMS extrait automatiquement les liens reçus par SMS, détecte les indicateurs de piège et évalue les risques d'escroquerie avec précision.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Onglets Principaux
tab1, tab2, tab3 = st.tabs([
    "📥 **Analyseur de SMS**",
    "📊 **Moteur IA & Dataset**",
    "🇧🇯 **Signalement & Urgence Bénin**"
])

# --- TAB 1 : ANALYSEUR ---
with tab1:
    st.markdown(
        "<h3 style='font-family: Roboto; font-weight: 700; color: #0f172a;'> Collez votre message ci-dessous</h3>",
        unsafe_allow_html=True)

    sms_input = st.text_area(
        "SMS complet à évaluer :",
        height=130,
        placeholder="Exemple : URGENT ! Votre compte Mobile Money est bloqué. Mettez à jour vos identifiants sur http://momo-benin-verification.top pour éviter la suspension."
    )

    if st.button("🚀 Analyser avec SentiSMS", type="primary"):
        if not sms_input.strip():
            st.warning("Veuillez d'abord coller le texte d'un SMS.")
        else:
            extracted_urls = extract_urls_from_text(sms_input)
            text_risk_score, found_kw = analyze_sms_text(sms_input)

            url_risk_score = 0
            features_dict = None
            detected_url = None

            if extracted_urls:
                detected_url = extracted_urls[0]
                features_dict = extract_24_features(detected_url)
                features_df = pd.DataFrame([features_dict])
                url_risk_score = model.predict_proba(features_df)[0][1] * 100
                global_risk_score = (url_risk_score * 0.6) + (text_risk_score * 0.4)
            else:
                global_risk_score = text_risk_score

            st.divider()

            col_res, col_score = st.columns([2, 1])

            with col_res:
                if global_risk_score >= 60:
                    st.error("🚨 **DIAGNOSTIC : SMISHING / ESCROQUERIE AVÉRÉE**")
                    st.markdown("""
                    <p style='color: #0f172a; font-size: 1.05rem; font-weight: 600;'>
                    <strong>Consignes de sécurité :</strong><br>
                    ❌ Ne cliquez sur aucun lien dans ce SMS.<br>
                    ❌ Ne communiquez aucun code secret OTP ou code PIN Mobile Money.<br>
                    🗑️ Signaler immédiatement ce message.
                    </p>
                    """, unsafe_allow_html=True)
                elif global_risk_score >= 30:
                    st.warning("⚠️ **DIAGNOSTIC : SMS SUSPECT / SOYEZ VIGILANT**")
                    st.markdown("""
                    <p style='color: #0f172a; font-size: 1.05rem; font-weight: 600;'>
                    Le message contient une incitation d'urgence ou des caractéristiques d'URL atypiques.
                    </p>
                    """, unsafe_allow_html=True)
                else:
                    st.success("✅ **DIAGNOSTIC : SMS LÉGITIME (FAIBLE RISQUE)**")
                    st.markdown("""
                    <p style='color: #0f172a; font-size: 1.05rem; font-weight: 600;'>
                    🔒 Aucun indicateur de menace évident détecté sur ce message.
                    </p>
                    """, unsafe_allow_html=True)

            with col_score:
                st.metric(label="Score Global de Risque", value=f"{global_risk_score:.1f} %")
                st.progress(int(global_risk_score))

            st.divider()

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("""
                <div class='senticard'>
                    <h5>📄 Analyse Textuelle & Lexicale</h5>
                """, unsafe_allow_html=True)
                st.write(f"• **Incitations à l'urgence :** {text_risk_score} %")
                if found_kw:
                    st.write(f"• **Mots-clés détectés :** `{', '.join(found_kw)}`")
                else:
                    st.write("• **Mots-clés suspects :** Aucun détecté.")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_d2:
                st.markdown("""
                <div class='senticard'>
                    <h5>🔗 Analyse Heuristique de l'URL</h5>
                """, unsafe_allow_html=True)
                if detected_url:
                    st.write(f"• **Lien extrait :** `{detected_url}`")
                    st.write(f"• **Risque ML de l'URL :** {url_risk_score:.1f} %")
                    st.write(
                        f"• **Protocole Sécurisé HTTPS :** {'Oui ✅' if features_dict['is_https'] == 1 else 'Non (Risqué) ⚠️'}")
                    st.write(
                        f"• **Extension / TLD Suspect :** {'Oui ⚠️' if features_dict['is_suspicious_tld'] == 1 else 'Non ✅'}")
                else:
                    st.write("• **Lien extrait :** Aucune URL détectée dans ce message.")
                st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2 : MOTEUR IA ---
with tab2:
    st.markdown(
        "<h3 style='font-family: Outfit; font-weight: 700; color: #0f172a;'>📊 Architecture du Modèle SentiSMS</h3>",
        unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Dataset d'Entraînement", f"{train_size:,} URL", "PhishTank & Tranco")
    c2.metric("Moteur Machine Learning", "Random Forest", "100 Arbres")
    c3.metric("Analyse Multimodale", "SMS + URL", "Score Combiné")

# --- TAB 3 : SIGNALEMENT BÉNIN ---
with tab3:
    st.markdown(
        "<h3 style='font-family: Outfit; font-weight: 700; color: #0f172a;'>🇧🇯 Dispositif Institutionnel au Bénin</h3>",
        unsafe_allow_html=True)
    st.markdown("""
    <div class="senticard">
        <h5>🏛️ Organismes Référents</h5>
        <p><strong>• ASIN Bénin :</strong> Agence des Systèmes d'Information et du Numérique.</p>
        <p><strong>• CNIN :</strong> Centre Nationale d'Investigations Numériques.</p>
        <p><strong>• Police Républicaine :</strong> Brigade Spéciale de Lutte Contre la Cybercriminalité.</p>
        <p>Si vous êtes sur le réseau MTN Bénin , vous pouvez composer le code *880*419# ou écrire à alert_arnaque@mtn.com pour dénoncer le numéro suspect.</p>
    </div>
    """, unsafe_allow_html=True)