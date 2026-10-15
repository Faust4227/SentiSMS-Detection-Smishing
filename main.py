import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from build_url_dataset import extract_24_features

# 1. Configuration de la page
st.set_page_config(
    page_title="Système - Détection Smishing Bénin",
    page_icon="🛡️",
    layout="wide"
)

# 2. Style CSS personnalisé (Inspiré de Bootstrap)
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .bs-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Barre latérale (Sidebar)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shield.png", width=80)
    st.title("🎓 Soutenance de Projet")
    st.markdown("**Thème :** Détection de Smishing via Machine Learning & Analyse d'URL")
    st.markdown("**Présenté par :** Faustine TCHOROPA")
    st.divider()

    st.subheader("⚙️ Fiche Technique ML")
    st.write("• **Modèle :** Random Forest Classifier")
    st.write("• **Dataset :** PhishTank + Tranco Top List")
    st.write("• **Indicateurs (Features) :** 24 Caractéristiques avancées")
    st.write("• **Environnement :** Python / Streamlit")
    st.divider()
    st.info(
        "💡 Système basé sur 24 indicateurs de risque (entropie, TLDs suspects, mots-clés, punycode, structure d'hôte).")

# 4. En-tête principal
st.markdown("""
    <div class="main-header">
        <h1>🛡️ Plateforme Anti-Smishing & Analyse de Risque</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">
            Système intelligent de détection d'URL frauduleuses par Apprentissage Automatique.
        </p>
    </div>
""", unsafe_allow_html=True)


# 5. Charger le dataset enrichi et entraîner le modèle
@st.cache_resource
def load_trained_model():
    df_train = pd.read_csv('url_dataset/train.csv')

    # Séparation des features (X) et de la cible (y)
    X_train = df_train.drop(columns=['url', 'label'])
    y_train = df_train['label']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model, len(df_train), X_train.columns


model, train_size, feature_names = load_trained_model()

# 6. Navigation par Onglets
tab1, tab2 = st.tabs(["🔍 Analyseur d'URL", "🇧🇯 Signalement & Prévention (Bénin)"])

with tab1:
    st.subheader("Analyse d'une URL suspecte")

    user_url = st.text_input("🔗 Collez l'URL reçue par SMS :",
                             placeholder="ex: http://secure-login.bank-update.com/verify")

    if st.button("🚀 Lancer l'Analyse", type="primary"):
        if not user_url.strip():
            st.warning("Veuillez saisir une URL avant de lancer l'analyse.")
        else:
            # Extraction des 24 indicateurs sur l'URL saisie
            features_dict = extract_24_features(user_url)
            features_df = pd.DataFrame([features_dict])

            prediction = model.predict(features_df)[0]
            prob_risk = model.predict_proba(features_df)[0][1] * 100

            st.divider()

            col_res, col_score = st.columns([2, 1])

            with col_res:
                if prediction == 1:
                    st.error("🚨 **DIAGNOSTIC : SMISHING / URL FRAUDULEUSE**")
                    st.markdown(
                        "⚠️ **Alerte :** L'algorithme a détecté des caractéristiques de risque élevées sur cette URL.")
                else:
                    st.success("✅ **DIAGNOSTIC : URL LÉGITIME (SÛRE)**")
                    st.markdown("🔒 L'URL présente les caractéristiques d'un domaine standard.")

            with col_score:
                st.metric(label="Niveau de Risque Calculé", value=f"{prob_risk:.1f} %")
                st.progress(int(prob_risk))

            st.divider()

            # Extrait de quelques indicateurs clés pour la démonstration devant le jury
            st.subheader("📋 Principaux Indicateurs de Risque Extraits (sur 24)")

            data_show = {
                "Indicateur": [
                    "Longueur de l'URL",
                    "Présence d'une adresse IP",
                    "Protocole Sécurisé (HTTPS)",
                    "Nombre de sous-domaines",
                    "Mots-clés de piège détectés",
                    "TLD / Extension suspecte",
                    "Entropie du domaine (Complexité)"
                ],
                "Valeur relevée": [
                    f"{features_dict['url_length']} caractères",
                    "Oui (Suspect) ⚠️" if features_dict['has_ip'] == 1 else "Non ✅",
                    "Non (Risqué) ⚠️" if features_dict['is_https'] == 0 else "Oui ✅",
                    features_dict['num_subdomains'],
                    features_dict['keyword_count'],
                    "Oui ⚠️" if features_dict['is_suspicious_tld'] == 1 else "Non ✅",
                    f"{features_dict['domain_entropy']:.2f}"
                ]
            }
            st.table(pd.DataFrame(data_show))

with tab2:
    st.subheader("🇧🇯 Cadre de Sensibilisation & Signalement au Bénin")

    st.markdown("""
    <div class="bs-card">
        <h4>📢 Pourquoi est-il vital de signaler les SMS frauduleux ?</h4>
        <p>
            Le <strong>smishing</strong> (phishing par SMS) est aujourd'hui un vecteur majeur d'escroquerie financière au Bénin, ciblant le <em>Mobile Money</em> et le banking en ligne. 
            <strong>Chaque signalement permet de :</strong>
        </p>
        <ul>
            <li>Bloquer la propagation des attaques sur le réseau télécom national.</li>
            <li>Alimenter la base d'informations des autorités pour neutraliser les cybercriminels.</li>
            <li>Protéger les usagers contre les pertes financières.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_benin1, col_benin2 = st.columns(2)

    with col_benin1:
        st.markdown("""
        <div class="bs-card">
            <h5>🏛️ Organismes Référents au Bénin</h5>
            <p><strong>• ASIN Bénin :</strong> Agence Nationale de la Sécurité des Systèmes d'Information.</p>
            <p><strong>• CNIN :</strong> Commission Nationale de l'Informatique et des Libertés.</p>
            <p><strong>• Police Républicaine (Lutte contre la Cybercriminalité) :</strong> Pour le dépôt de plainte en cas de préjudice.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_benin2:
        st.markdown("""
        <div class="bs-card">
            <h5>🛡️ Que faire en cas de réception d'un SMS suspect ?</h5>
            <ol>
                <li><strong>Ne pas cliquer</strong> sur le lien.</li>
                <li><strong>Ne jamais fournir</strong> son code secret Mobile Money ou de carte bancaire.</li>
                <li>Faire une <strong>capture d'écran</strong> du SMS et du numéro émetteur.</li>
                <li>Signaler au service client de votre opérateur télécom.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)