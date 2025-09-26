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
    from db import db
except ImportError:
    st.error("❌ Impossible de se connecter à la base de données MongoDB")

@safewatch_app(title="Réglementations - RiskRadar")
def main():
    # CSS spécifique pour la lisibilité du texte en blanc clair
    st.markdown("""
    <style>
    .stCaption {
        color: #f1f5f9 !important;
    }
    .stMarkdown p {
        color: #f1f5f9 !important;
    }
    .regulation-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #dc2626;
        transition: all 0.3s ease;
    }
    .regulation-card:hover {
        background: rgba(220, 38, 38, 0.1);
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(220, 38, 38, 0.2);
    }
    .region-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    .region-eu {
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .region-us {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .region-cn {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .region-fr {
        background: rgba(139, 92, 246, 0.2);
        color: #8b5cf6;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    .impact-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    .impact-high {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .impact-medium {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    .impact-low {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(220, 38, 38, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📋 Réglementations Surveillées")
    st.caption("Base de données des réglementations suivies par RiskRadar")

    # Statistiques de la base de données
    try:
        # Compter les réglementations dans la collection
        regulations_count = db.regulations.count_documents({})

        # Statistiques par région (approximation basée sur des mots-clés)
        eu_count = db.regulations.count_documents({"$text": {"$search": "europe european union GDPR"}})
        us_count = db.regulations.count_documents({"$text": {"$search": "united states america california"}})
        cn_count = db.regulations.count_documents({"$text": {"$search": "china chinese cybersecurity"}})
        fr_count = db.regulations.count_documents({"$text": {"$search": "france french loi"}})

        # Afficher les statistiques
        st.markdown("### 📊 Statistiques de la Base de Données")
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <h3 style="color: #dc2626; margin: 0;">📈 Total</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{regulations_count}</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Réglementations</p>
            </div>
            <div class="stat-card">
                <h3 style="color: #3b82f6; margin: 0;">🇪🇺 Europe</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{eu_count}</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">GDPR, AI Act...</p>
            </div>
            <div class="stat-card">
                <h3 style="color: #22c55e; margin: 0;">🇺🇸 États-Unis</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{us_count}</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">CCPA, CPRA...</p>
            </div>
            <div class="stat-card">
                <h3 style="color: #ef4444; margin: 0;">🇨🇳 Chine</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{cn_count}</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Cybersecurity Law...</p>
            </div>
            <div class="stat-card">
                <h3 style="color: #8b5cf6; margin: 0;">🇫🇷 France</h3>
                <h2 style="color: #f1f5f9; margin: 0.5rem 0;">{fr_count}</h2>
                <p style="color: #f1f5f9; opacity: 0.7; margin: 0;">Lois nationales...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"⚠️ Impossible d'accéder aux statistiques: {e}")
        regulations_count = 0

    # Données de démonstration des principales réglementations surveillées
    laws_data = [
        {
            "name": "RGPD - Règlement Général sur la Protection des Données",
            "id": "EU-2016/679",
            "date": "25 mai 2018",
            "status": "Actif",
            "region": "UE",
            "impact": "Élevé",
            "description": "Réglementation européenne sur la protection des données personnelles",
            "sectors": ["Tous secteurs", "Digital", "Manufacturing"],
            "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
        },
        {
            "name": "California Consumer Privacy Act (CCPA)",
            "id": "US-CCPA-2020",
            "date": "1 janvier 2020",
            "status": "Actif",
            "region": "US-CA",
            "impact": "Moyen",
            "description": "Loi californienne sur la confidentialité des consommateurs",
            "sectors": ["Digital", "E-commerce", "Manufacturing"],
            "url": "https://oag.ca.gov/privacy/ccpa"
        },
        {
            "name": "Loi Cybersécurité Chinoise",
            "id": "CN-CSL-2017",
            "date": "1 juin 2017",
            "status": "Actif",
            "region": "CN",
            "impact": "Élevé",
            "description": "Loi chinoise sur la cybersécurité et la protection des données",
            "sectors": ["Technologie", "Manufacturing", "Infrastructure"],
            "url": "http://www.npc.gov.cn/npc/xinwen/2016-11/07/content_2001605.htm"
        },
        {
            "name": "AI Act - Règlement sur l'Intelligence Artificielle",
            "id": "EU-AI-2024",
            "date": "1 août 2024",
            "status": "En vigueur",
            "region": "UE",
            "impact": "Très élevé",
            "description": "Premier cadre réglementaire mondial pour l'IA",
            "sectors": ["IA", "Automobile", "Aéronautique", "Manufacturing"],
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206"
        },
        {
            "name": "Règlement Automobile Type-Approval (WP.29)",
            "id": "EU-AUTO-2020",
            "date": "1 janvier 2021",
            "status": "Actif",
            "region": "UE",
            "impact": "Élevé",
            "description": "Réglementations de sécurité automobile et homologation",
            "sectors": ["Automobile", "Équipementiers"],
            "url": "https://unece.org/transport/vehicle-regulations"
        },
        {
            "name": "Aerospace Standards (AS/EN 9100)",
            "id": "AERO-9100",
            "date": "Révision continue",
            "status": "Actif",
            "region": "International",
            "impact": "Élevé",
            "description": "Normes de qualité pour l'industrie aéronautique",
            "sectors": ["Aéronautique", "Défense", "Spatial"],
            "url": "https://www.sae.org/standards/content/as9100d/"
        }
    ]

    # Filtres
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_region = st.selectbox(
            "🌍 Filtrer par région",
            ["Toutes", "UE", "US-CA", "CN", "International"],
            key="region_filter"
        )

    with col2:
        selected_impact = st.selectbox(
            "⚡ Filtrer par impact",
            ["Tous", "Très élevé", "Élevé", "Moyen", "Faible"],
            key="impact_filter"
        )

    with col3:
        selected_sector = st.selectbox(
            "🏭 Filtrer par secteur",
            ["Tous", "Automobile", "Aéronautique", "Manufacturing", "Digital"],
            key="sector_filter"
        )

    # Appliquer les filtres
    filtered_laws = laws_data.copy()

    if selected_region != "Toutes":
        filtered_laws = [law for law in filtered_laws if law["region"] == selected_region]

    if selected_impact != "Tous":
        filtered_laws = [law for law in filtered_laws if law["impact"] == selected_impact]

    if selected_sector != "Tous":
        filtered_laws = [law for law in filtered_laws if selected_sector in law["sectors"]]

    st.markdown(f"### 📋 Réglementations ({len(filtered_laws)} résultats)")

    # Affichage des cartes de lois filtrées
    for i, law in enumerate(filtered_laws):
        # Déterminer la couleur selon la région
        if law["region"] == "UE":
            region_class = "region-eu"
        elif law["region"] == "US-CA":
            region_class = "region-us"
        elif law["region"] == "CN":
            region_class = "region-cn"
        else:
            region_class = "region-fr"

        # Déterminer la couleur selon l'impact
        if law["impact"] == "Très élevé":
            impact_class = "impact-high"
            impact_icon = "🔴"
        elif law["impact"] == "Élevé":
            impact_class = "impact-high"
            impact_icon = "🟠"
        elif law["impact"] == "Moyen":
            impact_class = "impact-medium"
            impact_icon = "🟡"
        else:
            impact_class = "impact-low"
            impact_icon = "🟢"

        st.markdown(f"""
        <div class="regulation-card">
            <h3 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">{law['name']}</h3>
            <p style="color: #f1f5f9; margin: 0.2rem 0; font-size: 0.9rem; opacity: 0.8;">{law['description']}</p>
            
            <div style="margin: 0.5rem 0;">
                <strong style="color: #f1f5f9;">ID:</strong> <code style="color: #fbbf24;">{law['id']}</code> | 
                <strong style="color: #f1f5f9;">Date:</strong> {law['date']} | 
                <strong style="color: #f1f5f9;">Statut:</strong> {law['status']}
            </div>
            
            <div style="margin: 0.5rem 0;">
                <span class="region-badge {region_class}">🌍 {law['region']}</span>
                <span class="impact-badge {impact_class}">{impact_icon} {law['impact']}</span>
            </div>
            
            <div style="margin: 0.5rem 0;">
                <strong style="color: #f1f5f9;">Secteurs:</strong> {', '.join(law['sectors'])}
            </div>
            
            <div style="margin: 0.5rem 0;">
                <a href="{law['url']}" target="_blank" style="color: #fbbf24; text-decoration: none;">
                    🔗 Voir le texte officiel
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not filtered_laws:
        st.info("ℹ️ Aucune réglementation ne correspond aux filtres sélectionnés")

    # Section d'intégration avec le système d'analyse
    st.markdown("---")
    st.markdown("### 🤖 Intégration Système d'Analyse")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Analyser avec LLM", type="primary", use_container_width=True):
            st.info("🔄 Redirection vers l'analyse temps réel...")
            st.switch_page("pages/indicators_list.py")

    with col2:
        if st.button("📊 Voir Base MongoDB", type="secondary", use_container_width=True):
            try:
                # Afficher un échantillon de la vraie base de données
                with st.expander("🗄️ Échantillon Base de Données", expanded=True):
                    sample_regulations = list(db.regulations.find().limit(3))

                    if sample_regulations:
                        for reg in sample_regulations:
                            # Nettoyer l'affichage (supprimer _id pour la lisibilité)
                            if '_id' in reg:
                                del reg['_id']
                            st.json(reg)
                    else:
                        st.warning("📭 Aucune réglementation trouvée dans la base")

            except Exception as e:
                st.error(f"❌ Erreur d'accès à MongoDB: {e}")

    # Bouton retour
    st.markdown("---")
    if st.button("⬅️ Retour à l'accueil", type="secondary"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()
