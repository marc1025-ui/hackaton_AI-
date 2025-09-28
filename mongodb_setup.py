from pymongo import MongoClient
from datetime import datetime
import json

def setup_database():
    try:
        # Connexion
        client = MongoClient("mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc")

        # Créer la database
        db = client["hackathon_regulations"]
        
        # Collection 1 : Stockage des données réglementaires externes scrapées
        regulations = db["regulations"]
        # Rôle : Contient toutes les réglementations collectées depuis les sites web
        # (CBAM, CSRD, EUDR, sanctions, droits de douane)
        # Structure : titre, contenu, région, secteurs, dates, embeddings
        # Collection 2 : Profil de l'entreprise Hutchinson  
        hutchinson = db["hutchinson"]
        # Rôle : Stocke les informations internes de l'entreprise
        # (présence géographique, matières premières, clients, fournisseurs)
        # Utilisé pour matcher les réglementations avec l'activité réelle

        # Collection 3 : Résultats des analyses d'impact calculées par l'IA
        risk_analysis = db["risk_analysis"]
        # Rôle : Sauvegarde les conclusions intelligentes du système
        # (scores de risque, niveaux d'impact, recommandations, zones affectées)
        # Évite de recalculer les mêmes analyses avec Ollama
        
        # Insertion des données réglementaires depuis le fichier JSON allégé
        regulations_data = [
            {
                "nom_loi": "Regulation (EU) 2024/1347 of the European Parliament and of the Council of 14 May 2024",
                "lien_loi": "https://eur-lex.europa.eu/eli/reg/2024/1347/oj/eng",
                "id_loi": "32024R1347",
                "date_publication": datetime(2024, 5, 22),
                "type": "Reglement",
                "texte": "REGULATION (EU) 2024/1347 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 14 May 2024 on standards for the qualification of third-country nationals... [TEXTE COMPLET DISPONIBLE VIA LE LIEN]",
                "date_effet": datetime(2024, 6, 11),
                "date_vigueur": datetime(2026, 7, 1),
                "pays_concernes": ["UE"],
                "secteurs": ["Tous secteurs", "Services", "Immigration"],
                "created_at": datetime.now()
            },
            {
                "nom_loi": "Directive (EU) 2025/1 of the European Parliament and of the Council of 27 November 2024",
                "lien_loi": "https://eur-lex.europa.eu/eli/dir/2025/1/oj/eng",
                "id_loi": "32025L0001",
                "date_publication": datetime(2025, 1, 8),
                "type": "Directive",
                "texte": "DIRECTIVE (EU) 2025/1 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 27 November 2024... [TEXTE COMPLET DISPONIBLE VIA LE LIEN]",
                "date_effet": datetime(2025, 1, 28),
                "date_vigueur": None,
                "pays_concernes": ["UE"],
                "secteurs": ["Tous secteurs", "Digital", "Manufacturing"],
                "created_at": datetime.now()
            },
            # NOUVELLE LOI 1 - Réglementation sur les émissions automobiles (TRÈS pertinente pour Hutchinson)
            {
                "nom_loi": "Regulation (EU) 2025/892 on Automotive Sealing Systems and Emission Standards",
                "lien_loi": "https://eur-lex.europa.eu/eli/reg/2025/892/oj/eng",
                "id_loi": "32025R0892",
                "date_publication": datetime(2025, 3, 15),
                "type": "Reglement",
                "texte": """REGULATION (EU) 2025/892 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 15 March 2025 on automotive sealing systems and emission standards for vehicles manufactured in or imported into the European Union.

ARTICLE 1 - SCOPE
This regulation applies to all manufacturers of automotive sealing systems, vibration control components, and fluid transfer systems used in vehicles with internal combustion engines or hybrid powertrains operating within the European Union territory, including France, Germany, Poland, and Spain.

ARTICLE 2 - OBLIGATIONS FOR MANUFACTURERS  
Manufacturers of sealing systems utilizing natural rubber, synthetic rubber, or elastomer compounds must ensure their products meet enhanced leak-proof standards to prevent hydrocarbon emissions. Companies operating manufacturing facilities must implement certified quality control processes at all production sites.

ARTICLE 3 - MATERIAL RESTRICTIONS
The use of certain chemicals and plastics in automotive sealing applications is restricted. Manufacturers using steel, aluminum, and composite materials in sealing assemblies must provide environmental impact assessments for their supply chain operations, particularly when sourcing from China, India, or Brazil.

ARTICLE 4 - SANCTIONS AND PENALTIES
Non-compliance with this regulation shall result in the following sanctions:
- Administrative fines up to €2.5 million per manufacturing facility found in violation
- Additional penalties of €500 per non-compliant vehicle component placed on the market
- Temporary suspension of manufacturing authorization for periods up to 12 months for repeated violations
- Criminal proceedings may be initiated against company executives for willful non-compliance, with imprisonment up to 2 years

ARTICLE 5 - IMPLEMENTATION
This regulation enters into force on July 1, 2025, and applies to all automotive suppliers with more than 50 employees across their global operations.""",
                "date_effet": datetime(2025, 7, 1),
                "date_vigueur": datetime(2025, 7, 1),
                "pays_concernes": ["UE", "France", "Germany", "Poland", "Spain"],
                "secteurs": ["Automotive", "Manufacturing", "Sealing Systems"],
                "created_at": datetime.now()
            },
            # NOUVELLE LOI 2 - Réglementation aérospatiale (pertinente pour Hutchinson Aerospace)
            {
                "nom_loi": "Federal Aviation Regulation 145.67 - Aircraft Vibration Control Systems",
                "lien_loi": "https://www.faa.gov/regulations_policies/faa_regulations/",
                "id_loi": "FAR145067",
                "date_publication": datetime(2025, 4, 8),
                "type": "Federal Regulation",
                "texte": """FEDERAL AVIATION REGULATION 145.67 - AIRCRAFT VIBRATION CONTROL SYSTEMS

SECTION A - APPLICABILITY
This regulation applies to all manufacturers and maintenance organizations producing or servicing aircraft vibration control systems, shock absorbers, and anti-vibration components for commercial aviation operating in United States airspace.

SECTION B - MANUFACTURING REQUIREMENTS
Companies manufacturing aircraft sealing systems and vibration dampers must maintain FAA-certified facilities. All shock absorber components using synthetic rubber, steel, or aluminum construction must undergo rigorous testing protocols. Manufacturing operations in the United States, Mexico, or any other location serving U.S. aircraft must comply with these standards.

SECTION C - QUALITY ASSURANCE
Aerospace manufacturers must implement continuous monitoring of their supply chain, especially when sourcing materials from international suppliers. Components manufactured in facilities located in China, South Korea, or India require additional certification processes.

SECTION D - VIOLATIONS AND ENFORCEMENT
Violations of this regulation will result in:
- Civil penalties ranging from $25,000 to $500,000 per violation depending on severity
- Suspension of manufacturing certificates for up to 18 months
- Criminal prosecution for willful violations may result in fines up to $5 million and imprisonment for up to 5 years for responsible persons
- Immediate grounding of affected aircraft if safety violations are identified

SECTION E - EFFECTIVE DATE
This regulation becomes effective September 1, 2025, and applies retroactively to components manufactured after January 1, 2025.""",
                "date_effet": datetime(2025, 9, 1),
                "date_vigueur": datetime(2025, 9, 1),
                "pays_concernes": ["United States", "Mexico"],
                "secteurs": ["Aerospace", "Manufacturing", "Vibration Control"],
                "created_at": datetime.now()
            },
            # NOUVELLE LOI 3 - Réglementation sur l'industrie pharmaceutique (PAS du tout pour Hutchinson)
            {
                "nom_loi": "Directive (EU) 2025/456 on Pharmaceutical Manufacturing Standards",
                "lien_loi": "https://eur-lex.europa.eu/eli/dir/2025/456/oj/eng",
                "id_loi": "32025L0456",
                "date_publication": datetime(2025, 2, 20),
                "type": "Directive",
                "texte": """DIRECTIVE (EU) 2025/456 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 20 February 2025 on pharmaceutical manufacturing standards and clinical trial protocols.

ARTICLE 1 - SCOPE
This directive establishes harmonized standards for pharmaceutical companies engaged in drug development, clinical testing, and manufacturing of medicinal products for human use within the European Union.

ARTICLE 2 - MANUFACTURING REQUIREMENTS  
Pharmaceutical manufacturers must maintain sterile production environments and implement Good Manufacturing Practice (GMP) protocols. All facilities producing active pharmaceutical ingredients, tablets, capsules, or injectable medications must undergo annual inspections.

ARTICLE 3 - CLINICAL TRIAL OVERSIGHT
Companies conducting clinical trials must ensure patient safety protocols and obtain proper ethical committee approval. All research involving human subjects must comply with Helsinki Declaration principles.

ARTICLE 4 - SANCTIONS
Non-compliance results in:
- Monetary fines up to €10 million or 2% of annual worldwide turnover, whichever is higher
- Suspension of manufacturing licenses for up to 24 months
- Criminal prosecution for endangering patient safety, with imprisonment up to 7 years
- Mandatory product recalls at company expense

ARTICLE 5 - IMPLEMENTATION
This directive must be transposed into national law by December 31, 2025.""",
                "date_effet": datetime(2025, 12, 31),
                "date_vigueur": datetime(2026, 1, 1),
                "pays_concernes": ["UE"],
                "secteurs": ["Pharmaceutique", "Healthcare", "Clinical Research"],
                "created_at": datetime.now()
            }
        ]
        
        # Insérer les réglementations
        result_regulations = regulations.insert_many(regulations_data)
        print(f"✅ {len(result_regulations.inserted_ids)} réglementations insérées")
        
        # Profil Hutchinson
        hutchinson_profile = {
            "company_info": {
                "name": "Groupe Hutchinson",
                "sectors": ["Automotive", "Aerospace", "Industry", "Railway"],
                "headquarters": "France",
                "main_business": "sealing_systems_vibration_control"
            },
            
            "geographical_presence": [
                "France", "China", "United States", "Germany", "Poland", 
                "Spain", "Brazil", "Mexico", "India", "South Korea"
            ],
            
            "business_activities": {
                "automotive": ["sealing_systems", "vibration_control", "fluid_transfer", "gaskets", "hoses"],
                "aerospace": ["sealing_systems", "shock_absorbers", "vibration_dampers"],
                "industry": ["anti_vibration", "sealing", "rubber_components"],
                "railway": ["vibration_control", "sealing_systems"]
            },
            
            "typical_materials": [
                "natural_rubber", "synthetic_rubber", "steel", 
                "aluminum", "plastics", "chemicals", "elastomers", "composites"
            ],

            "specific_products": [
                "automotive_seals", "vibration_isolators", "shock_absorbers",
                "fluid_hoses", "gaskets", "dampers", "anti_vibration_mounts"
            ],

            "regulatory_focus": [
                "automotive_emissions", "aircraft_safety", "material_compliance",
                "manufacturing_standards", "environmental_regulations"
            ],
            
            "total_sites": 88,
            "created_at": datetime.now()
        }

        result_hutchinson = hutchinson.insert_one(hutchinson_profile)
        print(f"✅ Profil Hutchinson créé ! Document ID: {result_hutchinson.inserted_id}")
        
        # Créer des index pour optimiser les requêtes
        regulations.create_index("id_loi", unique=True)
        regulations.create_index("date_publication")
        regulations.create_index("type")
        regulations.create_index("pays_concernes")
        print("✅ Index créés sur la collection regulations")
        
        # Vérifier la connexion
        print(f"✅ Collections disponibles: {db.list_collection_names()}")
        print(f"✅ Nombre total de réglementations: {regulations.count_documents({})}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    setup_database()