#!/usr/bin/env python3
"""
Nettoyage et initialisation propre de la base MongoDB pour tester le matching
"""

from pymongo import MongoClient
from datetime import datetime

def clean_and_setup_database():
    """Nettoie la base et recrée les données de test pour le matching"""

    try:
        # Connexion MongoDB
        CONNECTION_STRING = "mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc"
        client = MongoClient(CONNECTION_STRING)
        db = client["hackathon_regulations"]

        print("🗑️ NETTOYAGE DE LA BASE...")

        # Supprimer toutes les collections existantes
        db.regulations.drop()
        db.hutchinson.drop()
        db.risk_analysis.drop()
        print("✅ Collections supprimées")

        print("\n📊 CRÉATION DES DONNÉES DE TEST...")

        # Réglementations de test - PROPRES et ciblées pour Hutchinson
        regulations_test = [
            # LOI 1 - TRÈS PERTINENTE pour Hutchinson Automotive
            {
                "nom_loi": "Regulation (EU) 2025/892 on Automotive Sealing Systems",
                "id_loi": "EU2025_892",
                "type": "Reglement",
                "date_publication": datetime(2025, 3, 15),
                "date_effet": datetime(2025, 7, 1),
                "date_vigueur": datetime(2025, 7, 1),
                "pays_concernes": ["France", "Germany", "Poland", "Spain"],
                "secteurs": ["Automotive", "Manufacturing"],
                "texte": """REGULATION on automotive sealing systems and emission standards.
                
SCOPE: Manufacturers of sealing systems, vibration control components, fluid transfer systems using natural rubber, synthetic rubber, steel, aluminum.

OBLIGATIONS: Enhanced leak-proof standards, certified quality control at production sites in France, Germany, Poland.

SANCTIONS: Administrative fines up to €2.5 million per facility + €500 per non-compliant component + suspension up to 12 months.""",
                "mots_cles": ["sealing", "automotive", "rubber", "steel", "aluminum", "vibration", "manufacturing"],
                "sanctions": "€2.5M per facility + €500 per component",
                "impact_financier": "HIGH",
                "created_at": datetime.now()
            },

            # LOI 2 - TRÈS PERTINENTE pour Hutchinson Aerospace
            {
                "nom_loi": "Federal Aviation Regulation 145.67 - Aircraft Vibration Control",
                "id_loi": "FAR145_067",
                "type": "Federal Regulation",
                "date_publication": datetime(2025, 4, 8),
                "date_effet": datetime(2025, 9, 1),
                "date_vigueur": datetime(2025, 9, 1),
                "pays_concernes": ["United States", "Mexico"],
                "secteurs": ["Aerospace", "Aviation"],
                "texte": """FEDERAL AVIATION REGULATION for aircraft vibration control systems.

SCOPE: Manufacturers of shock absorbers, anti-vibration components using synthetic rubber, steel, aluminum.

REQUIREMENTS: FAA-certified facilities, supply chain monitoring for China, South Korea, India components.

PENALTIES: $25,000 to $500,000 per violation + manufacturing certificate suspension up to 18 months + criminal prosecution possible.""",
                "mots_cles": ["aircraft", "vibration", "shock_absorbers", "aerospace", "rubber", "steel"],
                "sanctions": "$25K-$500K + suspension 18 months",
                "impact_financier": "HIGH",
                "created_at": datetime.now()
            },

            # LOI 3 - MOYENNEMENT PERTINENTE (géographie mais pas secteur)
            {
                "nom_loi": "CBAM Regulation 2023/956 - Carbon Border Adjustment",
                "id_loi": "CBAM2023_956",
                "type": "Reglement",
                "date_publication": datetime(2023, 10, 1),
                "date_effet": datetime(2024, 10, 1),
                "date_vigueur": datetime(2026, 1, 1),
                "pays_concernes": ["France", "Germany", "Poland", "Spain"],
                "secteurs": ["Manufacturing", "Import", "Export"],
                "texte": """CARBON BORDER ADJUSTMENT MECHANISM for imports.

SCOPE: Importers of carbon-intensive goods including steel, aluminum from China, India, Brazil.

OBLIGATIONS: Carbon content reporting, CBAM certificates purchase, emissions verification.

SANCTIONS: €10-100 per tonne CO2 equivalent + import restrictions.""",
                "mots_cles": ["carbon", "import", "steel", "aluminum", "China", "emissions"],
                "sanctions": "€10-100 per tonne CO2",
                "impact_financier": "MEDIUM",
                "created_at": datetime.now()
            },

            # LOI 4 - PAS PERTINENTE du tout (secteur pharmaceutique)
            {
                "nom_loi": "Directive (EU) 2025/456 on Pharmaceutical Manufacturing",
                "id_loi": "EU2025_456",
                "type": "Directive",
                "date_publication": datetime(2025, 2, 20),
                "date_effet": datetime(2025, 12, 31),
                "date_vigueur": datetime(2026, 1, 1),
                "pays_concernes": ["UE"],
                "secteurs": ["Pharmaceutical", "Healthcare"],
                "texte": """PHARMACEUTICAL manufacturing standards for drug development.

SCOPE: Companies in clinical trials, sterile production, active pharmaceutical ingredients.

REQUIREMENTS: GMP protocols, sterile environments, patient safety protocols.

SANCTIONS: €10 million or 2% annual turnover + license suspension 24 months.""",
                "mots_cles": ["pharmaceutical", "drugs", "clinical", "sterile", "GMP"],
                "sanctions": "€10M or 2% turnover",
                "impact_financier": "LOW",
                "created_at": datetime.now()
            }
        ]

        # Insérer les réglementations
        result_regs = db.regulations.insert_many(regulations_test)
        print(f"✅ {len(result_regs.inserted_ids)} réglementations insérées")

        # Profil Hutchinson EXACT
        hutchinson_profile = {
            "company_info": {
                "name": "Groupe Hutchinson",
                "sectors": ["Automotive", "Aerospace", "Industry", "Railway"],
                "headquarters": "France",
                "main_business": "sealing_systems_vibration_control"
            },
            "geographical_presence": [
                "France", "Germany", "Poland", "Spain", "United States", "Mexico",
                "China", "Brazil", "India", "South Korea"
            ],
            "business_activities": {
                "automotive": ["sealing_systems", "vibration_control", "fluid_transfer", "gaskets"],
                "aerospace": ["shock_absorbers", "vibration_dampers", "sealing_systems"],
                "industry": ["anti_vibration", "sealing", "rubber_components"]
            },
            "materials": [
                "natural_rubber", "synthetic_rubber", "steel", "aluminum",
                "plastics", "elastomers", "composites"
            ],
            "keywords_matching": [
                "sealing", "vibration", "automotive", "aerospace", "rubber",
                "steel", "aluminum", "shock_absorbers", "manufacturing"
            ],
            "created_at": datetime.now()
        }

        result_hutch = db.hutchinson.insert_one(hutchinson_profile)
        print(f"✅ Profil Hutchinson créé: {result_hutch.inserted_id}")

        # Créer les index
        db.regulations.create_index("id_loi", unique=True)
        db.regulations.create_index("pays_concernes")
        db.regulations.create_index("secteurs")
        db.regulations.create_index("mots_cles")
        print("✅ Index créés")

        print(f"\n📊 RÉSUMÉ:")
        print(f"• Réglementations totales: {db.regulations.count_documents({})}")
        print(f"• Collections: {db.list_collection_names()}")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NETTOYAGE ET SETUP BASE MONGODB")
    print("=" * 50)

    if clean_and_setup_database():
        print("\n✅ BASE PRÊTE POUR LES TESTS DE MATCHING !")
        print("\nDonnées créées:")
        print("• 2 lois TRÈS pertinentes (Automotive + Aerospace)")
        print("• 1 loi MOYENNEMENT pertinente (CBAM)")
        print("• 1 loi NON pertinente (Pharmaceutique)")
        print("• Profil Hutchinson complet")
    else:
        print("❌ Échec du setup")
