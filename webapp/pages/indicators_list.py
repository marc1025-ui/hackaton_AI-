import streamlit as st
import sys
import os
import json
import glob
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from safewatch_ui.layout import safewatch_app

# Importer les modules d'analyse réglementaire
try:
    from rag_with_llm import RegulatoryRiskRAGWithLLM, get_hutchinson_profile
except ImportError:
    st.error("❌ Impossible d'importer les modules d'analyse. Vérifiez que les fichiers sont présents.")
    st.stop()

def load_latest_analysis():
    """
    Charge la dernière analyse sauvegardée depuis la collection risk_analysis de MongoDB
    """
    try:
        # Importer la connexion MongoDB
        from db import db
        risk_analysis = db["risk_analysis"]

        # Chercher la dernière analyse dans la collection
        latest_analysis = risk_analysis.find_one(
            sort=[("analysis_timestamp", -1)]  # Tri décroissant par date
        )

        if not latest_analysis:
            return None

        # Convertir le format MongoDB vers le format UI attendu
        ui_data = {
            "indicators": latest_analysis.get("analysis_results", []),
            "metadata": latest_analysis.get("metadata", {}),
        }

        # Mettre à jour les métadonnées avec les infos MongoDB
        ui_data["metadata"]["company_name"] = latest_analysis.get("company_name", "Hutchinson")
        ui_data["metadata"]["total_indicators"] = len(ui_data["indicators"])
        ui_data["metadata"]["llm_used"] = True
        ui_data["metadata"]["model"] = latest_analysis.get("llm_model", "llama2")

        # Formatage de la date
        timestamp = latest_analysis.get("analysis_timestamp")
        if timestamp:
            formatted_timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
        else:
            formatted_timestamp = "Date inconnue"

        return {
            "data": ui_data,
            "source": "MongoDB risk_analysis",
            "timestamp": formatted_timestamp,
            "document_id": str(latest_analysis.get("_id", "Unknown")),
            "query_used": latest_analysis.get("query_used", ""),
            "mongodb_doc": latest_analysis  # Garder le document complet pour référence
        }

    except Exception as e:
        st.error(f"Erreur lors du chargement depuis MongoDB: {e}")
        return None

@safewatch_app(title="Analyse Temps Réel - RiskRadar")
def main():
    # CSS spécifique pour les indicateurs
    st.markdown("""
    <style>
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(220, 38, 38, 0.2);
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        background: rgba(220, 38, 38, 0.1);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(220, 38, 38, 0.2);
    }
    .law-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #dc2626;
        transition: all 0.3s ease;
    }
    .law-card:hover {
        background: rgba(220, 38, 38, 0.1);
        transform: translateX(5px);
    }
    .impact-high { border-left-color: #ef4444; }
    .impact-medium { border-left-color: #f59e0b; }
    .impact-low { border-left-color: #22c55e; }
    .loading-spinner {
        border: 3px solid rgba(220, 38, 38, 0.3);
        border-top: 3px solid #dc2626;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 10px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .last-update-badge {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        border: 1px solid rgba(34, 197, 94, 0.3);
        display: inline-block;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🚀 Analyse Temps Réel - Hutchinson")
    st.caption("Surveillance intelligente des risques réglementaires avec IA")

    # Initialiser les données par défaut si pas déjà en session
    if 'analysis_results' not in st.session_state:
        # Charger automatiquement la dernière analyse sauvegardée depuis MongoDB
        latest_analysis = load_latest_analysis()
        if latest_analysis:
            st.session_state['analysis_results'] = latest_analysis['data']
            st.session_state['analysis_timestamp'] = latest_analysis['timestamp']
            st.session_state['analysis_source'] = f"MongoDB risk_analysis (Doc ID: {latest_analysis['document_id'][:8]}...)"
            st.session_state['is_fresh_analysis'] = False
            st.session_state['mongodb_source'] = True
        else:
            # Pas d'analyse précédente trouvée
            st.session_state['analysis_results'] = None
            st.session_state['show_no_data_message'] = True

    # Boutons d'action
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("🔄 Actualiser l'Analyse LLM", type="primary", use_container_width=True):
            # Déclencher une nouvelle analyse
            with st.spinner("🤖 Nouvelle analyse en cours avec Ollama Llama2..."):
                try:
                    # Récupérer le profil Hutchinson
                    company_profile = get_hutchinson_profile()

                    if not company_profile:
                        st.error("❌ Impossible de récupérer le profil Hutchinson")
                        st.stop()

                    # Initialiser le système RAG avec LLM
                    rag = RegulatoryRiskRAGWithLLM("ollama")

                    # Requête spécifique pour Hutchinson
                    specific_query = "réglementations automobile aéronautique caoutchouc polymères manufacturing industrie"

                    # Lancer l'analyse
                    ui_data = rag.get_ui_ready_data(company_profile, specific_query)

                    if "error" in ui_data:
                        st.error(f"❌ Erreur d'analyse: {ui_data['error']}")
                        return

                    # Stocker les nouveaux résultats dans la session
                    st.session_state['analysis_results'] = ui_data
                    st.session_state['analysis_timestamp'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    st.session_state['analysis_source'] = "Analyse fraîche (LLM)"
                    st.session_state['is_fresh_analysis'] = True
                    st.session_state['show_no_data_message'] = False

                    st.success("✅ Analyse actualisée ! Nouveaux résultats ci-dessous.")
                    st.experimental_rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

    with col2:
        if st.button("📊 Historique", use_container_width=True):
            # Afficher l'historique des analyses
            st.session_state['show_history'] = True

    with col3:
        if st.button("🔄 Recharger", use_container_width=True):
            # Recharger la dernière analyse depuis MongoDB
            latest_analysis = load_latest_analysis()
            if latest_analysis:
                st.session_state['analysis_results'] = latest_analysis['data']
                st.session_state['analysis_timestamp'] = latest_analysis['timestamp']
                st.session_state['analysis_source'] = f"Rechargé depuis MongoDB (Doc ID: {latest_analysis['document_id'][:8]}...)"
                st.session_state['is_fresh_analysis'] = False
                st.session_state['show_no_data_message'] = False
                st.success("🔄 Données rechargées depuis MongoDB risk_analysis")
                st.experimental_rerun()
            else:
                st.warning("⚠️ Aucune analyse trouvée dans MongoDB risk_analysis")

    # Affichage de l'historique si demandé
    if st.session_state.get('show_history', False):
        with st.expander("📈 Historique des Analyses MongoDB", expanded=True):
            try:
                from db import db
                risk_analysis = db["risk_analysis"]

                # Récupérer les 10 dernières analyses
                analyses = list(risk_analysis.find().sort("analysis_timestamp", -1).limit(10))

                if analyses:
                    st.success(f"📁 {len(analyses)} analyses trouvées dans MongoDB")

                    for i, analysis_doc in enumerate(analyses):
                        timestamp = analysis_doc.get("analysis_timestamp")
                        if timestamp:
                            formatted_time = timestamp.strftime('%d/%m/%Y à %H:%M')
                        else:
                            formatted_time = "Date inconnue"

                        doc_id = str(analysis_doc.get("_id", "Unknown"))
                        total_laws = analysis_doc.get("total_regulations_analyzed", 0)
                        company = analysis_doc.get("company_name", "Hutchinson")

                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**{i+1}.** {company} - {total_laws} lois analysées")
                            st.caption(f"📅 {formatted_time} | 🆔 Doc ID: {doc_id[:12]}...")

                        with col_b:
                            if st.button(f"Charger", key=f"load_mongo_{i}"):
                                try:
                                    # Convertir vers format UI
                                    ui_data = {
                                        "indicators": analysis_doc.get("analysis_results", []),
                                        "metadata": analysis_doc.get("metadata", {}),
                                    }

                                    # Mettre à jour métadonnées
                                    ui_data["metadata"]["company_name"] = company
                                    ui_data["metadata"]["total_indicators"] = total_laws
                                    ui_data["metadata"]["llm_used"] = True
                                    ui_data["metadata"]["model"] = analysis_doc.get("llm_model", "llama2")

                                    st.session_state['analysis_results'] = ui_data
                                    st.session_state['analysis_timestamp'] = formatted_time
                                    st.session_state['analysis_source'] = f"MongoDB (Doc ID: {doc_id[:8]}...)"
                                    st.session_state['is_fresh_analysis'] = False
                                    st.session_state['show_history'] = False
                                    st.success(f"✅ Analyse du {formatted_time} chargée")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Erreur chargement: {e}")
                else:
                    st.info("📭 Aucune analyse trouvée dans MongoDB risk_analysis")
                    st.markdown("""
                    **Pour créer des données :**
                    1. Cliquez sur "🔄 Actualiser l'Analyse LLM"
                    2. Le système sauvegardera automatiquement dans MongoDB
                    3. Les analyses apparaîtront ici pour consultation future
                    """)

            except Exception as e:
                st.error(f"Erreur accès MongoDB: {e}")

            if st.button("❌ Fermer l'historique"):
                st.session_state['show_history'] = False
                st.experimental_rerun()

    # Affichage des résultats (par défaut ou actualisés)
    if st.session_state.get('analysis_results'):
        ui_data = st.session_state['analysis_results']
        timestamp = st.session_state.get('analysis_timestamp', 'Inconnu')
        source = st.session_state.get('analysis_source', 'Source inconnue')
        is_fresh = st.session_state.get('is_fresh_analysis', False)

        # Badge de statut
        if is_fresh:
            st.markdown("""
            <div class="last-update-badge">
                ✨ Analyse fraîche - Données actualisées
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="last-update-badge">
                📁 {source}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### 📊 Résultats de l'Analyse ({timestamp})")

        # Métadonnées de l'analyse
        metadata = ui_data.get("metadata", {})
        indicators = ui_data.get("indicators", [])

        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #f59e0b; margin: 0;">📈 Lois Identifiées</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{}</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Réglementations pertinentes</p>
            </div>
            """.format(len(indicators)), unsafe_allow_html=True)

        with col2:
            if indicators:
                avg_financial = sum(law.get('impact_financial', 0) for law in indicators) / len(indicators)
                color = "#ef4444" if avg_financial >= 7 else "#f59e0b" if avg_financial >= 5 else "#22c55e"
            else:
                avg_financial = 0
                color = "#22c55e"

            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {color}; margin: 0;">💰 Impact Financier</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{avg_financial:.1f}/10</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Risque moyen</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if indicators:
                avg_reputation = sum(law.get('impact_reputation', 0) for law in indicators) / len(indicators)
                color = "#ef4444" if avg_reputation >= 7 else "#f59e0b" if avg_reputation >= 5 else "#22c55e"
            else:
                avg_reputation = 0
                color = "#22c55e"

            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {color}; margin: 0;">🎯 Impact Réputation</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{avg_reputation:.1f}/10</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Risque d'image</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            if indicators:
                avg_operational = sum(law.get('impact_operational', 0) for law in indicators) / len(indicators)
                color = "#ef4444" if avg_operational >= 7 else "#f59e0b" if avg_operational >= 5 else "#22c55e"
            else:
                avg_operational = 0
                color = "#22c55e"

            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {color}; margin: 0;">⚙️ Impact Opérationnel</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{avg_operational:.1f}/10</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Complexité mise en œuvre</p>
            </div>
            """, unsafe_allow_html=True)

        # Niveau d'alerte global
        if indicators:
            global_impact = (avg_financial + avg_reputation + avg_operational) / 3
            if global_impact >= 7:
                alert_level = "🔴 CRITIQUE"
                alert_color = "#ef4444"
            elif global_impact >= 5:
                alert_level = "🟠 ÉLEVÉ"
                alert_color = "#f59e0b"
            elif global_impact >= 3:
                alert_level = "🟡 MODÉRÉ"
                alert_color = "#fbbf24"
            else:
                alert_level = "🟢 FAIBLE"
                alert_color = "#22c55e"

            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center; border: 2px solid {alert_color};">
                <h2 style="color: {alert_color}; margin: 0;">🚨 Niveau d'Alerte Global: {alert_level}</h2>
                <p style="color: #f1f5f9; margin: 0.5rem 0;">Score global: {global_impact:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)

        # Liste détaillée des lois
        if indicators:
            st.markdown("### 📋 Réglementations Identifiées par le LLM")

            for i, law in enumerate(indicators, 1):
                # Déterminer la classe CSS selon l'impact
                max_impact = max(
                    law.get('impact_financial', 0),
                    law.get('impact_reputation', 0),
                    law.get('impact_operational', 0)
                )

                if max_impact >= 7:
                    card_class = "law-card impact-high"
                elif max_impact >= 5:
                    card_class = "law-card impact-medium"
                else:
                    card_class = "law-card impact-low"

                st.markdown(f"""
                <div class="{card_class}">
                    <h4 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">{i}. {law.get('law_name', 'Nom non disponible')}</h4>
                    <p style="color: #f1f5f9; margin: 0.2rem 0; font-size: 0.9rem;">
                        <strong>🔗 URL:</strong> <a href="{law.get('law_url', '#')}" target="_blank" style="color: #fbbf24;">{law.get('law_url', 'Non disponible')}</a>
                    </p>
                    <p style="color: #f1f5f9; margin: 0.2rem 0;">
                        <strong>📅 Échéance:</strong> {law.get('deadline', 'Non définie')} | 
                        <strong>🎯 Secteur:</strong> {law.get('sector_match', 'Non spécifié')}
                    </p>
                    <div style="display: flex; gap: 1rem; margin: 0.5rem 0;">
                        <span style="color: #ef4444;">💰 {law.get('impact_financial', 0)}/10</span>
                        <span style="color: #f59e0b;">🎯 {law.get('impact_reputation', 0)}/10</span>
                        <span style="color: #22c55e;">⚙️ {law.get('impact_operational', 0)}/10</span>
                    </div>
                    <p style="color: #f1f5f9; margin: 0.2rem 0; font-style: italic; opacity: 0.8;">
                        📝 {law.get('notes', 'Aucune note disponible')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Aucune réglementation pertinente identifiée pour les activités de Hutchinson")
            st.markdown("""
            **Cela signifie que :**
            - Le LLM a correctement filtré les réglementations
            - Aucune loi pharmaceutique, agricole ou financière n'a été retournée
            - Le système fonctionne comme prévu pour exclure les secteurs non pertinents
            """)

    elif st.session_state.get('show_no_data_message', False):
        # Aucune donnée disponible - première utilisation
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(255, 255, 255, 0.05); border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: #f1f5f9;">🚀 Première Utilisation de RiskRadar</h3>
            <p style="color: #f1f5f9; opacity: 0.8;">
                Aucune analyse précédente trouvée.<br>
                Cliquez sur "🔄 Actualiser l'Analyse LLM" pour lancer votre première analyse
            </p>
            <div style="margin: 1rem 0;">
                <span style="color: #22c55e;">✅ Automobile</span> •
                <span style="color: #22c55e;">✅ Aéronautique</span> •
                <span style="color: #22c55e;">✅ Manufacturing</span><br>
                <span style="color: #ef4444;">❌ Pharmaceutique</span> •
                <span style="color: #ef4444;">❌ Agriculture</span> •
                <span style="color: #ef4444;">❌ Finance</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Bouton retour
    st.markdown("---")
    if st.button("⬅️ Retour à l'accueil", type="secondary"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()
