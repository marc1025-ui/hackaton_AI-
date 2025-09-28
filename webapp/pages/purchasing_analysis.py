import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
import os
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import math

# Ajouter le répertoire parent au path pour importer les modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Ajouter aussi le répertoire webapp au path pour les imports locaux
webapp_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(webapp_dir)

try:
    from safewatch_ui.layout import safewatch_app
except ImportError:
    # Fallback si l'import ne fonctionne pas
    def safewatch_app(title="Service Achats - RiskRadar"):
        def decorator(func):
            return func
        return decorator

# Données intégrées pour éviter la base de données
SAMPLE_REGULATIONS = [
    {
        "id": "reg-eu-cbam-001",
        "title": "CBAM — Déclaration trimestrielle des importations (acier/alu)",
        "jurisdiction": "UE",
        "rtype": "CBAM",
        "phase": "adopté",
        "date_published": "2023-10-01",
        "deadline": "2025-12-31T00:00:00Z",
        "summary": "Mécanisme d'ajustement carbone aux frontières. Déclarations trimestrielles obligatoires pour certains HS.",
        "impact_hutchinson": "Élevé - Produits acier/aluminium utilisés dans les joints"
    },
    {
        "id": "reg-eu-eudr-001",
        "title": "EUDR — Traçabilité caoutchouc naturel (géolocalisation)",
        "jurisdiction": "UE",
        "rtype": "EUDR",
        "phase": "appliqué",
        "date_published": "2024-06-01",
        "deadline": "2025-12-30T00:00:00Z",
        "summary": "Exclusion du marché UE des produits issus de déforestation. Géolocalisation des plantations requise.",
        "impact_hutchinson": "Critique - Caoutchouc naturel = matière première clé"
    },
    {
        "id": "reg-eu-csrd-001",
        "title": "CSRD — ESRS E1/E2 reporting extra-financier",
        "jurisdiction": "UE",
        "rtype": "CSRD",
        "phase": "appliqué",
        "date_published": "2024-01-01",
        "deadline": "2026-03-31T00:00:00Z",
        "summary": "Obligation de reporting de durabilité. Périmètre et indicateurs ESRS à publier annuellement.",
        "impact_hutchinson": "Moyen - Reporting groupe requis"
    },
    {
        "id": "reg-us-sanctions-001",
        "title": "Sanctions — Mise à jour liste entités (OFAC)",
        "jurisdiction": "USA",
        "rtype": "Sanctions",
        "phase": "appliqué",
        "date_published": "2025-01-15",
        "deadline": "2025-10-01T00:00:00Z",
        "summary": "Mise à jour de la liste SDN. Screening requis pour éviter transactions interdites.",
        "impact_hutchinson": "Élevé - Fournisseurs chinois à contrôler"
    },
    {
        "id": "reg-cn-reach-001",
        "title": "Chine — Nouvelle liste substances chimiques restreintes",
        "jurisdiction": "Chine",
        "rtype": "Chemicals",
        "phase": "projet",
        "date_published": "2025-08-01",
        "deadline": "2026-01-01T00:00:00Z",
        "summary": "Extension de la réglementation REACH chinoise à de nouveaux composés chimiques.",
        "impact_hutchinson": "Moyen - Sites de production chinois impactés"
    }
]

MATERIALS_DATA = [
    {"mat_id": "MAT-001", "libelle": "Acier laminé", "hs_code": "7208", "famille": "acier"},
    {"mat_id": "MAT-002", "libelle": "Aluminium brut", "hs_code": "7601", "famille": "aluminium"},
    {"mat_id": "MAT-003", "libelle": "Caoutchouc naturel", "hs_code": "4001", "famille": "caoutchouc"},
    {"mat_id": "MAT-004", "libelle": "Elastomères synthétiques", "hs_code": "4002", "famille": "polymères"},
    {"mat_id": "MAT-005", "libelle": "Composés chimiques", "hs_code": "2902", "famille": "chimie"}
]

SUPPLIERS_DATA = [
    {"nom": "Bridgestone Corp", "pays": "Japon", "materiau": "Caoutchouc naturel", "risque": "Faible", "score": 25},
    {"nom": "Michelin Plantations", "pays": "Brésil", "materiau": "Caoutchouc naturel", "risque": "Moyen", "score": 45},
    {"nom": "Thai Rubber Co", "pays": "Thaïlande", "materiau": "Caoutchouc naturel", "risque": "Élevé", "score": 75},
    {"nom": "Arcelor Mittal", "pays": "France", "materiau": "Acier laminé", "risque": "Faible", "score": 20},
    {"nom": "Baosteel Group", "pays": "Chine", "materiau": "Acier laminé", "risque": "Élevé", "score": 80},
    {"nom": "Norsk Hydro", "pays": "Norvège", "materiau": "Aluminium brut", "risque": "Faible", "score": 15},
    {"nom": "Chalco Aluminum", "pays": "Chine", "materiau": "Aluminium brut", "risque": "Élevé", "score": 85}
]

# Données étendues des fournisseurs avec coordonnées géographiques et émissions
SUPPLIERS_EXTENDED = [
    {
        "nom": "Bridgestone Corp",
        "pays": "Japon",
        "ville": "Tokyo",
        "materiau": "Caoutchouc naturel",
        "coordinates": [35.6762, 139.6503],
        "risque": "Faible",
        "score": 25,
        "emissions_co2_kg_tonne": 45,
        "certifie_iso14001": True,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 15000,
        "continent": "Asie"
    },
    {
        "nom": "Michelin Plantations",
        "pays": "Brésil",
        "ville": "São Paulo",
        "materiau": "Caoutchouc naturel",
        "coordinates": [-23.5505, -46.6333],
        "risque": "Moyen",
        "score": 45,
        "emissions_co2_kg_tonne": 78,
        "certifie_iso14001": True,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 22000,
        "continent": "Amérique du Sud"
    },
    {
        "nom": "Thai Rubber Co",
        "pays": "Thaïlande",
        "ville": "Bangkok",
        "materiau": "Caoutchouc naturel",
        "coordinates": [13.7563, 100.5018],
        "risque": "Élevé",
        "score": 75,
        "emissions_co2_kg_tonne": 120,
        "certifie_iso14001": False,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 8500,
        "continent": "Asie"
    },
    {
        "nom": "Arcelor Mittal",
        "pays": "France",
        "ville": "Dunkerque",
        "materiau": "Acier laminé",
        "coordinates": [51.0345, 2.3767],
        "risque": "Faible",
        "score": 20,
        "emissions_co2_kg_tonne": 35,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 45000,
        "continent": "Europe"
    },
    {
        "nom": "Baosteel Group",
        "pays": "Chine",
        "ville": "Shanghai",
        "materiau": "Acier laminé",
        "coordinates": [31.2304, 121.4737],
        "risque": "Élevé",
        "score": 80,
        "emissions_co2_kg_tonne": 150,
        "certifie_iso14001": False,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 67000,
        "continent": "Asie"
    },
    {
        "nom": "Norsk Hydro",
        "pays": "Norvège",
        "ville": "Oslo",
        "materiau": "Aluminium brut",
        "coordinates": [59.9139, 10.7522],
        "risque": "Faible",
        "score": 15,
        "emissions_co2_kg_tonne": 28,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 12000,
        "continent": "Europe"
    },
    {
        "nom": "Chalco Aluminum",
        "pays": "Chine",
        "ville": "Pékin",
        "materiau": "Aluminium brut",
        "coordinates": [39.9042, 116.4074],
        "risque": "Élevé",
        "score": 85,
        "emissions_co2_kg_tonne": 180,
        "certifie_iso14001": False,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 34000,
        "continent": "Asie"
    },
    {
        "nom": "Continental Rubber",
        "pays": "Allemagne",
        "ville": "Hanovre",
        "materiau": "Elastomères synthétiques",
        "coordinates": [52.3759, 9.7320],
        "risque": "Faible",
        "score": 30,
        "emissions_co2_kg_tonne": 52,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 18000,
        "continent": "Europe"
    },
    {
        "nom": "BASF Chemical",
        "pays": "Allemagne",
        "ville": "Ludwigshafen",
        "materiau": "Composés chimiques",
        "coordinates": [49.4814, 8.4451],
        "risque": "Moyen",
        "score": 40,
        "emissions_co2_kg_tonne": 65,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 9500,
        "continent": "Europe"
    },
    {
        "nom": "Dow Chemical India",
        "pays": "Inde",
        "ville": "Mumbai",
        "materiau": "Composés chimiques",
        "coordinates": [19.0760, 72.8777],
        "risque": "Élevé",
        "score": 88,
        "emissions_co2_kg_tonne": 195,
        "certifie_iso14001": False,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 14000,
        "continent": "Asie"
    },
    {
        "nom": "ThyssenKrupp Steel",
        "pays": "Allemagne",
        "ville": "Duisburg",
        "materiau": "Acier laminé",
        "coordinates": [51.4344, 6.7623],
        "risque": "Faible",
        "score": 25,
        "emissions_co2_kg_tonne": 38,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 38000,
        "continent": "Europe"
    },
    {
        "nom": "Repsol Chemicals",
        "pays": "Espagne",
        "ville": "Tarragone",
        "materiau": "Elastomères synthétiques",
        "coordinates": [41.1189, 1.2445],
        "risque": "Moyen",
        "score": 35,
        "emissions_co2_kg_tonne": 58,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 16000,
        "continent": "Europe"
    },
    {
        "nom": "Borealis Polymers",
        "pays": "Autriche",
        "ville": "Linz",
        "materiau": "Elastomères synthétiques",
        "coordinates": [48.3069, 14.2858],
        "risque": "Faible",
        "score": 28,
        "emissions_co2_kg_tonne": 48,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 21000,
        "continent": "Europe"
    },
    {
        "nom": "Aperam Stainless",
        "pays": "France",
        "ville": "Isbergues",
        "materiau": "Acier laminé",
        "coordinates": [50.6167, 2.4500],
        "risque": "Faible",
        "score": 22,
        "emissions_co2_kg_tonne": 32,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 28000,
        "continent": "Europe"
    },
    {
        "nom": "Alcoa Netherlands",
        "pays": "Pays-Bas",
        "ville": "Delfzijl",
        "materiau": "Aluminium brut",
        "coordinates": [53.3167, 6.9167],
        "risque": "Faible",
        "score": 18,
        "emissions_co2_kg_tonne": 26,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 35000,
        "continent": "Europe"
    },
    {
        "nom": "Pirelli Rubber Europe",
        "pays": "Italie",
        "ville": "Milan",
        "materiau": "Caoutchouc naturel",
        "coordinates": [45.4642, 9.1900],
        "risque": "Moyen",
        "score": 42,
        "emissions_co2_kg_tonne": 68,
        "certifie_iso14001": True,
        "certifie_cbam": False,
        "volume_annuel_tonnes": 19000,
        "continent": "Europe"
    },
    {
        "nom": "Orlen Petrochemicals",
        "pays": "Pologne",
        "ville": "Płock",
        "materiau": "Composés chimiques",
        "coordinates": [52.5467, 19.7064],
        "risque": "Moyen",
        "score": 38,
        "emissions_co2_kg_tonne": 62,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 24000,
        "continent": "Europe"
    },
    {
        "nom": "Covestro Polymers",
        "pays": "Allemagne",
        "ville": "Leverkusen",
        "materiau": "Composés chimiques",
        "coordinates": [51.0347, 7.0122],
        "risque": "Faible",
        "score": 30,
        "emissions_co2_kg_tonne": 55,
        "certifie_iso14001": True,
        "certifie_cbam": True,
        "volume_annuel_tonnes": 32000,
        "continent": "Europe"
    }
]

# Sites Hutchinson avec coordonnées
HUTCHINSON_SITES = {
    "Chalette-sur-Loing (Siège)": [48.0167, 2.7333],
    "Wrocław (Pologne)": [51.1079, 17.0385],
    "Shanghai (Chine)": [31.2304, 121.4737],
    "Birmingham (USA)": [33.5207, -86.8025],
    "São Paulo (Brésil)": [-23.5505, -46.6333],
    "Munich (Allemagne)": [48.1351, 11.5820]
}

# Modes de transport avec facteurs d'émission (kg CO2/tonne/km)
TRANSPORT_MODES = {
    "Route": {"factor": 0.08, "speed_kmh": 80, "icon": "🚛", "color": "orange"},
    "Train": {"factor": 0.025, "speed_kmh": 120, "icon": "🚂", "color": "green"},
    "Maritime": {"factor": 0.015, "speed_kmh": 25, "icon": "🚢", "color": "blue"},
    "Aérien": {"factor": 0.5, "speed_kmh": 800, "icon": "✈️", "color": "red"}
}

def months_to_deadline(iso_date: str | None) -> int | None:
    """Calcule les mois jusqu'à l'échéance"""
    if not iso_date:
        return None
    try:
        d = datetime.fromisoformat(iso_date.replace("Z",""))
        delta = (d.year - datetime.utcnow().year)*12 + (d.month - datetime.utcnow().month)
        return max(delta, 0)
    except Exception:
        return None

def score_regulation(reg: dict) -> int:
    """Calcule le score de criticité d'une réglementation"""
    CRIT_BASE = {"critique": 80, "élevé": 60, "moyen": 40, "faible": 20}

    phase = reg.get("phase", "projet")
    rtype = reg.get("rtype", "")

    # Heuristique de criticité
    crit = "moyen"
    if rtype in ("Sanctions", "CBAM"):
        crit = "élevé"
    if phase in ("appliqué",):
        crit = "critique"
    if phase in ("projet", "consultation"):
        crit = "moyen"

    base = CRIT_BASE.get(crit, 30)
    m = months_to_deadline(reg.get("deadline"))

    if m is None:
        return base
    if m <= 1:
        return min(100, base+20)
    if m <= 3:
        return min(100, base+10)
    return base

def calculate_transport_chain_emissions(supplier_coords, site_coords, transport_chain, volume_tonnes):
    """Calcule les émissions pour une chaîne de transport complexe"""
    total_distance = geodesic(supplier_coords, site_coords).kilometers
    total_emissions = 0
    total_time = 0

    if len(transport_chain) == 1:
        # Transport direct
        mode = transport_chain[0]
        mode_data = TRANSPORT_MODES[mode]
        emissions = total_distance * mode_data["factor"] * volume_tonnes
        time_hours = total_distance / mode_data["speed_kmh"]
        return emissions, time_hours, total_distance

    # Transport multi-modal - répartition approximative des distances
    if len(transport_chain) == 2:
        # Ex: Route -> Maritime ou Train -> Route
        distances = [total_distance * 0.3, total_distance * 0.7]
    elif len(transport_chain) == 3:
        # Ex: Route -> Maritime -> Train
        distances = [total_distance * 0.2, total_distance * 0.6, total_distance * 0.2]
    else:
        # Répartition égale
        distances = [total_distance / len(transport_chain)] * len(transport_chain)

    for i, mode in enumerate(transport_chain):
        mode_data = TRANSPORT_MODES[mode]
        segment_emissions = distances[i] * mode_data["factor"] * volume_tonnes
        segment_time = distances[i] / mode_data["speed_kmh"]
        total_emissions += segment_emissions
        total_time += segment_time

    return total_emissions, total_time, total_distance

def get_supplier_color(supplier, site_coords, transport_chain, volume_tonnes):
    """Détermine la couleur du marqueur basée sur les émissions carbone"""
    emissions, _, _ = calculate_transport_chain_emissions(
        supplier["coordinates"], site_coords, transport_chain, volume_tonnes
    )

    # Seuils d'émissions (kg CO2)
    if emissions < 5000:
        return "green"  # Faibles émissions
    elif emissions < 15000:
        return "orange"  # Émissions moyennes
    else:
        return "red"    # Émissions élevées

def get_auto_transport_chain(supplier_continent, site_continent):
    """Sélectionne automatiquement la chaîne de transport optimale selon les continents"""

    # Si même continent
    if supplier_continent == site_continent:
        if supplier_continent == "Europe":
            return ["Train"]  # Privilégier le train en Europe
        else:
            return ["Route"]  # Route pour autres continents

    # Transport intercontinental
    distance_mappings = {
        ("Europe", "Asie"): ["Train", "Maritime"],
        ("Asie", "Europe"): ["Route", "Maritime", "Train"],
        ("Europe", "Amérique du Sud"): ["Route", "Maritime", "Route"],
        ("Amérique du Sud", "Europe"): ["Route", "Maritime", "Train"],
        ("Europe", "Amérique du Nord"): ["Train", "Maritime", "Route"],
        ("Amérique du Nord", "Europe"): ["Route", "Maritime", "Train"],
        ("Asie", "Amérique du Nord"): ["Route", "Maritime", "Route"],
        ("Amérique du Nord", "Asie"): ["Route", "Maritime", "Route"],
        ("Asie", "Amérique du Sud"): ["Route", "Maritime", "Route"],
        ("Amérique du Sud", "Asie"): ["Route", "Maritime", "Route"]
    }

    # Retour par défaut si combinaison non trouvée
    return distance_mappings.get((supplier_continent, site_continent), ["Route", "Maritime", "Route"])

def get_site_continent(site_name):
    """Détermine le continent d'un site Hutchinson"""
    continent_mapping = {
        "Chalette-sur-Loing (Siège)": "Europe",
        "Wrocław (Pologne)": "Europe",
        "Shanghai (Chine)": "Asie",
        "Birmingham (USA)": "Amérique du Nord",
        "São Paulo (Brésil)": "Amérique du Sud",
        "Munich (Allemagne)": "Europe"
    }
    return continent_mapping.get(site_name, "Europe")

def calculate_multi_product_emissions(supplier, site_coords, transport_chain, product_volumes):
    """Calcule les émissions pour plusieurs produits combinés"""
    total_volume = sum(product_volumes.values())
    base_emissions, time_hours, distance = calculate_transport_chain_emissions(
        supplier["coordinates"], site_coords, transport_chain, total_volume
    )

    # Bonus/malus selon le volume (économies d'échelle)
    if total_volume > 500:
        efficiency_bonus = 0.9  # 10% de réduction pour gros volumes
    elif total_volume > 200:
        efficiency_bonus = 0.95  # 5% de réduction
    else:
        efficiency_bonus = 1.0

    transport_emissions = base_emissions * efficiency_bonus

    # Émissions de production par produit
    production_emissions = 0
    for product, volume in product_volumes.items():
        if product.lower() in supplier["materiau"].lower():
            production_emissions += supplier["emissions_co2_kg_tonne"] * volume

    return transport_emissions + production_emissions, time_hours, distance

@safewatch_app(title="Service Achats - RiskRadar")
def main():
    # CSS spécifique pour le service achats
    st.markdown("""
    <style>
    .procurement-header {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #dc2626;
        margin: 1rem 0;
    }
    .risk-high { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.1); }
    .risk-medium { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.1); }
    .risk-low { border-left-color: #10b981; background: rgba(16, 185, 129, 0.1); }
    
    .supplier-card {
        background: rgba(255, 255, 255, 0.08);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid rgba(220, 38, 38, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    # Header du service achats
    st.markdown("""
    <div class="procurement-header">
        <h1>🛒 Service Achats - Analyse des Risques Fournisseurs</h1>
        <p>Surveillance réglementaire pour la chaîne d'approvisionnement Hutchinson</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs pour organiser les fonctionnalités
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Tableau de Bord",
        "⚖️ Veille Réglementaire",
        "🏭 Analyse Fournisseurs",
        "📈 Rapports d'Impact",
        "🗺️ Carte Fournisseurs"
    ])

    with tab1:
        st.header("📊 Tableau de Bord des Risques")

        # Calcul des métriques clés
        regulations_df = pd.DataFrame(SAMPLE_REGULATIONS)
        regulations_df['score'] = regulations_df.apply(score_regulation, axis=1)

        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            critical_count = len(regulations_df[regulations_df['score'] >= 80])
            st.metric("🚨 Réglementations Critiques", critical_count, delta="+2 cette semaine")

        with col2:
            high_risk_suppliers = len([s for s in SUPPLIERS_DATA if s['score'] >= 70])
            st.metric("⚠️ Fournisseurs à Risque", high_risk_suppliers, delta="+1")

        with col3:
            avg_score = int(regulations_df['score'].mean())
            st.metric("📈 Score Moyen de Risque", f"{avg_score}/100", delta="-5 points")

        with col4:
            urgent_deadlines = len([r for r in SAMPLE_REGULATIONS if months_to_deadline(r.get('deadline', '')) and months_to_deadline(r.get('deadline', '')) <= 3])
            st.metric("⏰ Échéances Urgentes", urgent_deadlines, delta="3 mois")

        # Graphique de répartition des risques
        st.subheader("📊 Répartition des Scores de Risque")

        fig = px.histogram(
            regulations_df,
            x='score',
            nbins=10,
            title="Distribution des Scores de Risque Réglementaire",
            color_discrete_sequence=['#dc2626']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Top 5 des réglementations les plus critiques
        st.subheader("🔥 Top 5 Réglementations Prioritaires")
        top_regulations = regulations_df.nlargest(5, 'score')

        for _, reg in top_regulations.iterrows():
            risk_class = "risk-high" if reg['score'] >= 70 else "risk-medium" if reg['score'] >= 40 else "risk-low"
            st.markdown(f"""
            <div class="risk-card {risk_class}">
                <h4 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">{reg['title']}</h4>
                <p style="color: #f1f5f9; margin: 0.2rem 0;"><strong>Score:</strong> {reg['score']}/100 | <strong>Juridiction:</strong> {reg['jurisdiction']} | <strong>Phase:</strong> {reg['phase']}</p>
                <p style="color: #f1f5f9; margin: 0.2rem 0; font-size: 0.9rem;">{reg['impact_hutchinson']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.header("⚖️ Veille Réglementaire Active")

        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            selected_jurisdiction = st.selectbox(
                "🌍 Filtrer par juridiction",
                ["Toutes"] + list(set([r['jurisdiction'] for r in SAMPLE_REGULATIONS]))
            )
        with col2:
            selected_type = st.selectbox(
                "📋 Filtrer par type",
                ["Tous"] + list(set([r['rtype'] for r in SAMPLE_REGULATIONS]))
            )

        # Affichage des réglementations filtrées
        filtered_regs = SAMPLE_REGULATIONS
        if selected_jurisdiction != "Toutes":
            filtered_regs = [r for r in filtered_regs if r['jurisdiction'] == selected_jurisdiction]
        if selected_type != "Tous":
            filtered_regs = [r for r in filtered_regs if r['rtype'] == selected_type]

        st.subheader(f"📋 {len(filtered_regs)} réglementations trouvées")

        for reg in filtered_regs:
            score = score_regulation(reg)
            months_left = months_to_deadline(reg.get('deadline'))

            risk_class = "risk-high" if score >= 70 else "risk-medium" if score >= 40 else "risk-low"

            with st.expander(f"{'🚨' if score >= 70 else '⚠️' if score >= 40 else '✅'} {reg['title']} - Score: {score}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Juridiction:** {reg['jurisdiction']}")
                    st.write(f"**Type:** {reg['rtype']}")
                    st.write(f"**Phase:** {reg['phase']}")
                    st.write(f"**Publié le:** {reg['date_published']}")
                with col2:
                    if months_left:
                        st.write(f"**Échéance:** {months_left} mois restants")
                    st.write(f"**Score de risque:** {score}/100")
                    st.write(f"**Impact Hutchinson:** {reg['impact_hutchinson']}")

                st.write("**Résumé:**")
                st.write(reg['summary'])

    with tab3:
        st.header("🏭 Analyse des Fournisseurs par Matériau")

        # Sélection du matériau à analyser
        selected_material = st.selectbox(
            "🔍 Sélectionner un matériau critique",
            ["Caoutchouc naturel", "Acier laminé", "Aluminium brut", "Elastomères synthétiques", "Composés chimiques"]
        )

        # Filtrer les fournisseurs par matériau
        material_suppliers = [s for s in SUPPLIERS_DATA if selected_material.lower() in s['materiau'].lower()]

        if material_suppliers:
            st.subheader(f"📊 Fournisseurs de {selected_material}")

            # Graphique des scores de risque par pays
            suppliers_df = pd.DataFrame(material_suppliers)

            fig = px.scatter(
                suppliers_df,
                x='pays',
                y='score',
                size='score',
                color='risque',
                hover_data=['nom'],
                title=f"Scores de Risque - Fournisseurs {selected_material}",
                color_discrete_map={'Faible': '#10b981', 'Moyen': '#f59e0b', 'Élevé': '#ef4444'}
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#f1f5f9'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Liste détaillée des fournisseurs
            st.subheader("📋 Détail des Fournisseurs")

            for supplier in sorted(material_suppliers, key=lambda x: x['score'], reverse=True):
                risk_class = "risk-high" if supplier['score'] >= 70 else "risk-medium" if supplier['score'] >= 40 else "risk-low"

                st.markdown(f"""
                <div class="supplier-card {risk_class}">
                    <h4 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">
                        {supplier['nom']} ({supplier['pays']})
                    </h4>
                    <p style="color: #f1f5f9; margin: 0.2rem 0;">
                        <strong>Matériau:</strong> {supplier['materiau']} | 
                        <strong>Niveau de risque:</strong> {supplier['risque']} |
                        <strong>Score:</strong> {supplier['score']}/100
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"Aucun fournisseur trouvé pour {selected_material}")

    with tab4:
        st.header("📈 Rapports d'Impact Réglementaire")

        # Analyse d'impact par région
        st.subheader("🌍 Impact par Région Géographique")

        regions_impact = {}
        for reg in SAMPLE_REGULATIONS:
            jurisdiction = reg['jurisdiction']
            score = score_regulation(reg)
            if jurisdiction not in regions_impact:
                regions_impact[jurisdiction] = []
            regions_impact[jurisdiction].append(score)

        # Calculer les moyennes par région
        regions_avg = {region: sum(scores)/len(scores) for region, scores in regions_impact.items()}

        fig = px.bar(
            x=list(regions_avg.keys()),
            y=list(regions_avg.values()),
            title="Score de Risque Moyen par Région",
            color=list(regions_avg.values()),
            color_continuous_scale=['green', 'yellow', 'red']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Recommandations d'actions
        st.subheader("🎯 Recommandations d'Actions Prioritaires")

        recommendations = [
            {
                "priorite": "🚨 Urgent",
                "action": "Mise en conformité EUDR pour caoutchouc naturel",
                "deadline": "30 décembre 2025",
                "impact": "Critique - Risque d'exclusion du marché UE"
            },
            {
                "priorite": "⚠️ Important",
                "action": "Audit fournisseurs chinois (sanctions OFAC)",
                "deadline": "1 octobre 2025",
                "impact": "Élevé - Risque de sanctions financières"
            },
            {
                "priorite": "📋 Suivi",
                "action": "Préparation déclarations CBAM acier/aluminium",
                "deadline": "31 décembre 2025",
                "impact": "Moyen - Coûts additionnels d'importation"
            }
        ]

        for rec in recommendations:
            priority_class = "risk-high" if "Urgent" in rec['priorite'] else "risk-medium" if "Important" in rec['priorite'] else "risk-low"

            st.markdown(f"""
            <div class="risk-card {priority_class}">
                <h4 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">
                    {rec['priorite']} - {rec['action']}
                </h4>
                <p style="color: #f1f5f9; margin: 0.2rem 0;">
                    <strong>Échéance:</strong> {rec['deadline']} | <strong>Impact:</strong> {rec['impact']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab5:
        st.header("🗺️ Carte Dynamique des Fournisseurs")
        st.caption("Analyse géographique avec calcul d'empreinte carbone selon les modes de transport")

        # Mode de vue : 2D ou 3D Globe
        view_mode = st.radio(
            "🌍 Type de carte",
            ["🗺️ Vue 2D Classique", "🌐 Globe 3D Interactif"],
            horizontal=True
        )

        # Paramètres de simulation
        col1, col2 = st.columns(2)

        with col1:
            selected_site = st.selectbox(
                "🏭 Site Hutchinson de destination",
                list(HUTCHINSON_SITES.keys())
            )
            site_coords = HUTCHINSON_SITES[selected_site]
            site_continent = get_site_continent(selected_site)

        with col2:
            # NOUVEAU: Sélection multi-produits
            st.subheader("📦 Commande Multi-Produits")
            selected_products = st.multiselect(
                "Sélectionner les produits à commander",
                ["Caoutchouc naturel", "Acier laminé", "Aluminium brut", "Elastomères synthétiques", "Composés chimiques"],
                default=["Caoutchouc naturel"]
            )

        if not selected_products:
            st.error("⚠️ Veuillez sélectionner au moins un produit")
            return

        # Volumes pour chaque produit sélectionné
        st.subheader("⚖️ Volumes par Produit (tonnes)")
        product_volumes = {}
        cols = st.columns(len(selected_products))

        for i, product in enumerate(selected_products):
            with cols[i % len(cols)]:
                volume = st.number_input(
                    f"{product}",
                    min_value=1,
                    max_value=5000,
                    value=100,
                    step=10,
                    key=f"volume_{product}"
                )
                product_volumes[product] = volume

        total_volume = sum(product_volumes.values())
        st.info(f"📊 **Volume total:** {total_volume} tonnes")

        st.markdown("---")

        # Configuration des chaînes de transport
        st.subheader("🚚 Configuration des Modes de Transport")

        # Option transport automatique
        auto_transport = st.checkbox("🤖 Sélection automatique selon le continent", value=True)

        if auto_transport:
            # Transport sélectionné automatiquement
            st.info("🤖 **Mode automatique activé** - Le transport optimal sera choisi selon la géographie")
            selected_chain = None  # Will be determined per supplier
        else:
            # Transport manuel
            transport_chains = {
                "🚛 Route directe": ["Route"],
                "🚂 Train direct": ["Train"],
                "✈️ Aérien direct": ["Aérien"],
                "🚢 Maritime direct": ["Maritime"],
                "🚛➡️🚢 Route + Maritime": ["Route", "Maritime"],
                "🚂➡️🚢 Train + Maritime": ["Train", "Maritime"],
                "🚛➡️✈️ Route + Aérien": ["Route", "Aérien"],
                "🚂➡️✈️ Train + Aérien": ["Train", "Aérien"],
                "🚛➡️🚢➡️🚂 Route + Maritime + Train": ["Route", "Maritime", "Train"],
                "🚂➡️🚢➡️🚛 Train + Maritime + Route": ["Train", "Maritime", "Route"]
            }

            selected_chain_name = st.selectbox(
                "🔗 Choisir la chaîne de transport",
                list(transport_chains.keys())
            )
            selected_chain = transport_chains[selected_chain_name]

        # Calculs pour tous les fournisseurs pertinents
        supplier_results = []
        for supplier in SUPPLIERS_EXTENDED:
            # Vérifier si le fournisseur peut fournir au moins un des produits
            can_supply = any(product.lower() in supplier["materiau"].lower() for product in selected_products)

            if can_supply:
                # Déterminer le transport (auto ou manuel)
                if auto_transport:
                    transport_chain = get_auto_transport_chain(supplier["continent"], site_continent)
                else:
                    transport_chain = selected_chain

                # Calculer pour les produits que ce fournisseur peut livrer
                supplier_products = {
                    product: volume for product, volume in product_volumes.items()
                    if product.lower() in supplier["materiau"].lower()
                }

                if supplier_products:  # Si le fournisseur peut livrer au moins un produit
                    emissions, time_hours, distance = calculate_multi_product_emissions(
                        supplier, site_coords, transport_chain, supplier_products
                    )

                    supplier_results.append({
                        **supplier,
                        "transport_chain": transport_chain,
                        "products_supplied": list(supplier_products.keys()),
                        "volumes_supplied": supplier_products,
                        "emissions_transport": emissions - sum(supplier["emissions_co2_kg_tonne"] * vol for vol in supplier_products.values()),
                        "emissions_production": sum(supplier["emissions_co2_kg_tonne"] * vol for vol in supplier_products.values()),
                        "temps_transport_h": time_hours,
                        "distance_km": distance,
                        "emissions_totales": emissions,
                        "color": "green" if emissions < 8000 else "orange" if emissions < 20000 else "red"
                    })

        if supplier_results:
            if view_mode == "🌐 Globe 3D Interactif":
                # NOUVELLE CARTE 3D GLOBE
                st.subheader("🌐 Globe 3D Interactif")

                # Créer le globe 3D avec Plotly
                fig_globe = go.Figure()

                # Ajouter les fournisseurs sur le globe
                for supplier in supplier_results:
                    color = "#10b981" if supplier["color"] == "green" else "#f59e0b" if supplier["color"] == "orange" else "#ef4444"

                    fig_globe.add_trace(go.Scattergeo(
                        lon=[supplier["coordinates"][1]],
                        lat=[supplier["coordinates"][0]],
                        mode='markers+text',
                        marker=dict(
                            size=max(8, min(20, supplier["emissions_totales"] / 1000)),
                            color=color,
                            line=dict(width=2, color='white'),
                            sizemode='diameter'
                        ),
                        text=supplier["nom"],
                        textposition="top center",
                        textfont=dict(size=10, color='white'),
                        hovertemplate=(
                            f"<b>{supplier['nom']}</b><br>" +
                            f"📍 {supplier['ville']}, {supplier['pays']}<br>" +
                            f"📦 Produits: {', '.join(supplier['products_supplied'])}<br>" +
                            f"🚚 Transport: {' ➡️ '.join([TRANSPORT_MODES[mode]['icon'] + mode for mode in supplier['transport_chain']])}<br>" +
                            f"💨 Émissions: {supplier['emissions_totales']:.0f} kg CO2<br>" +
                            f"📏 Distance: {supplier['distance_km']:.0f} km<br>" +
                            f"{'🟢 CBAM Certifié' if supplier['certifie_cbam'] else '🔴 Non CBAM'}<br>" +
                            "<extra></extra>"
                        ),
                        name=f"Fournisseur {supplier['color'].capitalize()}"
                    ))

                # Ajouter le site Hutchinson
                fig_globe.add_trace(go.Scattergeo(
                    lon=[site_coords[1]],
                    lat=[site_coords[0]],
                    mode='markers+text',
                    marker=dict(size=15, color='#3b82f6', symbol='square'),
                    text="🏭 " + selected_site.split(" (")[0],
                    textposition="bottom center",
                    textfont=dict(size=12, color='white'),
                    name="Site Hutchinson"
                ))

                # Configuration du globe 3D
                fig_globe.update_layout(
                    title=f"🌐 Globe des Fournisseurs - {', '.join(selected_products)} vers {selected_site}",
                    geo=dict(
                        projection_type='orthographic',
                        showland=True,
                        landcolor='rgb(20, 30, 40)',
                        oceancolor='rgb(10, 15, 25)',
                        showocean=True,
                        countrycolor='rgb(60, 60, 60)',
                        coastlinecolor='rgb(100, 100, 100)',
                        showlakes=True,
                        lakecolor='rgb(10, 15, 25)'
                    ),
                    height=600,
                    paper_bgcolor='rgba(0,0,0,0.9)',
                    font_color='white'
                )

                st.plotly_chart(fig_globe, use_container_width=True)

            else:
                # CARTE 2D CLASSIQUE AMÉLIORÉE
                st.subheader("🗺️ Carte Interactive 2D")

                center_lat = (site_coords[0] + sum(s["coordinates"][0] for s in supplier_results)) / (len(supplier_results) + 1)
                center_lon = (site_coords[1] + sum(s["coordinates"][1] for s in supplier_results)) / (len(supplier_results) + 1)

                m = folium.Map(location=[center_lat, center_lon], zoom_start=2, tiles="CartoDB dark_matter")

                # Ajouter le site Hutchinson de destination
                folium.Marker(
                    location=site_coords,
                    popup=f"""
                    <b>🏭 {selected_site}</b><br>
                    Site Hutchinson de destination<br>
                    Produits: {', '.join(selected_products)}<br>
                    Volume total: {total_volume} tonnes
                    """,
                    icon=folium.Icon(color="blue", icon="industry", prefix="fa")
                ).add_to(m)

                # Ajouter les fournisseurs avec informations détaillées
                for supplier in supplier_results:
                    # Icône selon certification CBAM
                    icon_name = "certificate" if supplier["certifie_cbam"] else "truck"

                    popup_html = f"""
                    <b>{supplier['nom']}</b><br>
                    📍 {supplier['ville']}, {supplier['pays']}<br>
                    📦 Produits fournis: {', '.join(supplier['products_supplied'])}<br>
                    📏 Distance: {supplier['distance_km']:.0f} km<br>
                    🚚 Transport: {' ➡️ '.join([TRANSPORT_MODES[mode]['icon'] + mode for mode in supplier['transport_chain']])}<br>
                    ⏱️ Temps: {supplier['temps_transport_h']:.1f}h<br>
                    🌍 Émissions transport: {supplier['emissions_transport']:.0f} kg CO2<br>
                    🏭 Émissions production: {supplier['emissions_production']:.0f} kg CO2<br>
                    <b>💨 Total: {supplier['emissions_totales']:.0f} kg CO2</b><br>
                    {'✅ Certifié ISO14001' if supplier['certifie_iso14001'] else '❌ Non certifié ISO14001'}<br>
                    {'🟢 Certifié CBAM' if supplier['certifie_cbam'] else '🔴 Non certifié CBAM'}
                    """

                    folium.Marker(
                        location=supplier["coordinates"],
                        popup=folium.Popup(popup_html, max_width=350),
                        icon=folium.Icon(
                            color=supplier["color"],
                            icon=icon_name,
                            prefix="fa"
                        )
                    ).add_to(m)

                    # Ligne de transport avec style selon émissions
                    line_weight = 3 if supplier["color"] == "red" else 2
                    folium.PolyLine(
                        locations=[supplier["coordinates"], site_coords],
                        weight=line_weight,
                        color=supplier["color"],
                        opacity=0.8,
                        dash_array="5,5" if not supplier["certifie_cbam"] else None
                    ).add_to(m)

                # Légende améliorée
                legend_html = '''
                <div style="position: fixed; 
                            bottom: 50px; left: 50px; width: 220px; height: 160px; 
                            background-color: rgba(0,0,0,0.8); border:2px solid #dc2626; z-index:9999; 
                            font-size:12px; padding: 10px; color: white; border-radius: 10px">
                <p><b>🌍 Légende Carbone & CBAM</b></p>
                <p><i class="fa fa-circle" style="color:green"></i> < 8000 kg CO2 (Faible)</p>
                <p><i class="fa fa-circle" style="color:orange"></i> 8000-20000 kg CO2 (Moyen)</p>
                <p><i class="fa fa-circle" style="color:red"></i> > 20000 kg CO2 (Élevé)</p>
                <p>🟢 Ligne continue = CBAM certifié</p>
                <p>🔴 Ligne pointillée = Non CBAM</p>
                </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))

                # Afficher la carte
                map_data = st_folium(m, width=700, height=600)

            # Tableau de comparaison amélioré
            st.subheader("📊 Comparaison Détaillée des Fournisseurs")

            df_comparison = pd.DataFrame(supplier_results)
            df_comparison = df_comparison.sort_values("emissions_totales")

            # Affichage du tableau avec nouvelles colonnes
            display_df = df_comparison[[
                "nom", "pays", "products_supplied", "distance_km", "emissions_totales",
                "temps_transport_h", "certifie_cbam", "certifie_iso14001"
            ]].copy()

            display_df.columns = [
                "Fournisseur", "Pays", "Produits Fournis", "Distance (km)",
                "Émissions Totales (kg CO2)", "Temps (h)", "CBAM", "ISO 14001"
            ]

            # Conversion des listes en string pour l'affichage
            display_df["Produits Fournis"] = display_df["Produits Fournis"].apply(lambda x: ", ".join(x[:2]) + ("..." if len(x) > 2 else ""))

            st.dataframe(display_df, use_container_width=True)

            # Graphiques d'analyse
            col1, col2 = st.columns(2)

            with col1:
                # Graphique émissions par fournisseur
                fig_emissions = px.bar(
                    df_comparison.head(10),
                    x="nom",
                    y="emissions_totales",
                    color="color",
                    title="🔝 Top 10 Fournisseurs - Émissions CO2",
                    color_discrete_map={"green": "#10b981", "orange": "#f59e0b", "red": "#ef4444"}
                )
                fig_emissions.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#f1f5f9',
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_emissions, use_container_width=True)

            with col2:
                # Analyse CBAM vs Non-CBAM
                cbam_analysis = df_comparison.groupby('certifie_cbam')['emissions_totales'].mean()

                fig_cbam = px.pie(
                    values=cbam_analysis.values,
                    names=['Non CBAM', 'CBAM Certifié'],
                    title="📊 Répartition Émissions: CBAM vs Non-CBAM",
                    color_discrete_sequence=['#ef4444', '#10b981']
                )
                fig_cbam.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#f1f5f9'
                )
                st.plotly_chart(fig_cbam, use_container_width=True)

        else:
            st.warning(f"Aucun fournisseur trouvé pour les produits sélectionnés: {', '.join(selected_products)}")

    # Bouton retour
    st.markdown("---")
    if st.button("⬅️ Retour à l'accueil", type="secondary"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()
