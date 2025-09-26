import streamlit as st
import sys
import os
import json
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from safewatch_ui.layout import safewatch_app

# Importer les modules d'analyse réglementaire
try:
    from rag_with_llm import RegulatoryRiskRAGWithLLM, get_hutchinson_profile
except ImportError:
    st.error("❌ Impossible d'importer les modules d'analyse. Vérifiez que les fichiers sont présents dans le répertoire parent.")
    st.stop()

@safewatch_app(title="RiskRadar - Hutchinson")
def main():
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1), rgba(185, 28, 28, 0.05));
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(220, 38, 38, 0.2);
        text-align: center;
    }
    .riskradar-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(45deg, #dc2626, #f59e0b, #dc2626);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 2s ease-in-out infinite alternate;
        text-shadow: 0 0 20px rgba(220, 38, 38, 0.5);
        margin: 1rem 0;
    }
    @keyframes glow {
        from { filter: brightness(1); }
        to { filter: brightness(1.2); }
    }
    .hutchinson-logo {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
        z-index: 1000;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .hutchinson-logo:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
    }
    .subtitle {
        font-size: 1.3rem;
        color: #f9fafb;
        margin: 1rem 0 2rem 0;
        opacity: 0.9;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(220, 38, 38, 0.2);
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(220, 38, 38, 0.1);
        border-color: rgba(220, 38, 38, 0.4);
        box-shadow: 0 10px 30px rgba(220, 38, 38, 0.2);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #dc2626;
        margin-bottom: 1rem;
    }
    .feature-desc {
        color: #f9fafb;
        opacity: 0.8;
        line-height: 1.5;
    }
    .fire-emoji {
        animation: bounce 1s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    .status-success {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-warning {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    .status-error {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo Hutchinson
    st.markdown('<a href="https://www.hutchinson.com" target="_blank" class="hutchinson-logo">🔗 HUTCHINSON</a>', unsafe_allow_html=True)

    # Section héro avec RiskRadar
    st.markdown("""
    <div class="hero-section">
        <h1 class="riskradar-title">
            <span class="fire-emoji">🔥</span> RiskRadar <span class="fire-emoji">🔥</span>
        </h1>
        <p class="subtitle">
            <strong>🎯 Votre radar ultra-performant pour les risques réglementaires Hutchinson</strong><br>
            🤖 Détection intelligente • 📊 Analyse prédictive • ⚡ Action immédiate
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Récupérer le profil Hutchinson en temps réel
    try:
        company_profile = get_hutchinson_profile()
        if company_profile:
            # Afficher le profil Hutchinson actuel
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### 🏢 Profil Entreprise Actuel")
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                    <p style="color: #f1f5f9; margin: 0.2rem 0;"><strong>Nom:</strong> {company_profile.get('nom', 'Hutchinson')}</p>
                    <p style="color: #f1f5f9; margin: 0.2rem 0;"><strong>Secteurs:</strong> {company_profile.get('secteur', 'Non défini')}</p>
                    <p style="color: #f1f5f9; margin: 0.2rem 0;"><strong>Présence:</strong> {', '.join(company_profile.get('presence_geographique', [])[:4])}...</p>
                    <p style="color: #f1f5f9; margin: 0.2rem 0;"><strong>Matières:</strong> {', '.join(company_profile.get('matieres_premieres', [])[:4])}...</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Statut du système
                st.markdown("### 📊 Statut Système")
                st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <span class="status-badge status-success">✅ Ollama Connecté</span><br>
                    <span class="status-badge status-success">✅ MongoDB Actif</span><br>
                    <span class="status-badge status-success">✅ RAG Système OK</span><br>
                    <span class="status-badge status-warning">⚠️ LLM en Attente</span>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Erreur de connexion au système: {e}")

    # Grille des fonctionnalités
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon">📡</span>
            <div class="feature-title">Détection Radar</div>
            <div class="feature-desc">Surveillance temps réel des réglementations avec IA avancée pour anticiper tous les risques sectoriels</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <div class="feature-title">Analyse Flash LLM</div>
            <div class="feature-desc">Intelligence artificielle Ollama pour une évaluation instantanée des impacts sur les activités Hutchinson</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🌍</span>
            <div class="feature-title">Couverture Globale</div>
            <div class="feature-desc">Monitoring multi-régions (France, US, Chine, Allemagne) avec filtrage sectoriel automatique</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <div class="feature-title">Filtrage Intelligent</div>
            <div class="feature-desc">Exclusion automatique des secteurs non pertinents (pharma, agro, finance) - Focus automobile/aéronautique</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Boutons d'action avec analyse en temps réel
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Analyse Temps Réel", key="real_time_analysis", type="primary", use_container_width=True):
            st.switch_page("pages/indicators_list.py")

    with col2:
        if st.button("📋 Réglementations Suivies", key="regulations_list", type="secondary", use_container_width=True):
            st.switch_page("pages/laws_list.py")

    with col3:
        if st.button("📊 Historique Analyses", key="analysis_history", type="secondary", use_container_width=True):
            # Afficher les dernières analyses dans un expander
            with st.expander("📈 Dernières analyses sauvegardées", expanded=True):
                # Chercher les fichiers d'analyse récents
                try:
                    import glob
                    analysis_files = glob.glob(os.path.join(parent_dir, "hutchinson_analysis_*.json"))
                    analysis_files.sort(key=os.path.getmtime, reverse=True)

                    if analysis_files:
                        st.success(f"📁 {len(analysis_files)} analyses trouvées")

                        # Afficher les 3 dernières
                        for i, file_path in enumerate(analysis_files[:3]):
                            filename = os.path.basename(file_path)
                            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            st.markdown(f"**{i+1}.** `{filename}`")
                            st.caption(f"📅 Créé le {file_time.strftime('%d/%m/%Y à %H:%M')}")

                            # Bouton pour voir le contenu
                            if st.button(f"👀 Voir", key=f"view_{i}"):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)

                                    if 'indicators' in data and data['indicators']:
                                        st.json(data)
                                    else:
                                        st.info("📄 Analyse sans réglementations identifiées")
                                except Exception as e:
                                    st.error(f"Erreur lecture fichier: {e}")
                    else:
                        st.info("📭 Aucune analyse sauvegardée trouvée")
                        st.caption("💡 Lancez une analyse temps réel pour créer des données")

                except Exception as e:
                    st.error(f"Erreur recherche fichiers: {e}")

    # Section informations techniques
    with st.expander("🔧 Informations Techniques", expanded=False):
        st.markdown("""
        ### Configuration Système
        - **Modèle LLM:** Ollama Llama2 (local)
        - **Base de données:** MongoDB (collections: regulations, hutchinson, risk_analysis)
        - **Système RAG:** Vector search avec embeddings
        - **Filtrage:** Intelligence artificielle + profil entreprise
        - **Secteurs surveillés:** Automobile, Aéronautique, Manufacturing
        - **Exclusions automatiques:** Pharmaceutique, Agriculture, Finance
        """)

if __name__ == "__main__":
    main()
