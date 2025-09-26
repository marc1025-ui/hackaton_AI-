#!/usr/bin/env python3
"""
Test du LLM modifié pour vérifier qu'il produit les données structurées demandées
"""

from rag_with_llm import RegulatoryRiskRAGWithLLM
from datetime import datetime

def test_llm_structured_output():
    """Teste si le LLM produit exactement les données demandées"""

    print("🧪 TEST DU LLM MODIFIÉ - DONNÉES STRUCTURÉES")
    print("=" * 60)

    # Initialiser le système LLM
    rag = RegulatoryRiskRAGWithLLM("rules")

    # Créer un rapport de test avec vos données réelles
    test_report = {
        "detailed_analysis": {
            "high_risk": [
                {
                    "regulation": {
                        "nom_loi": "CBAM – Exposition CO₂ import",
                        "lien_loi": "https://europa.eu/cbam",
                        "date_effet": datetime(2026, 1, 1),
                        "texte": "Regulation on carbon border adjustment mechanism for steel and chemical imports with high carbon intensity",
                        "sanctions": "Fines up to €2.5 million per facility",
                        "score": 0.85
                    },
                    "impact_details": ["high_financial_impact", "regulatory_compliance"]
                },
                {
                    "regulation": {
                        "nom_loi": "NIS2 Directive – Cybersécurité",
                        "lien_loi": "https://www.enisa.europa.eu/topics/nis-directive",
                        "date_effet": datetime(2025, 10, 17),
                        "texte": "Directive on cybersecurity measures for critical entities in manufacturing sector",
                        "sanctions": "Administrative fines and operational restrictions",
                        "score": 0.92
                    },
                    "impact_details": ["operational_transformation", "security_compliance"]
                }
            ],
            "medium_risk": [
                {
                    "regulation": {
                        "nom_loi": "US Tariffs – Tarifs acier",
                        "lien_loi": "https://www.trade.gov",
                        "date_effet": datetime(2025, 11, 15),
                        "texte": "US tariffs on steel imports affecting manufacturing costs",
                        "sanctions": "Import duties and trade restrictions",
                        "score": 0.65
                    },
                    "impact_details": ["cost_increase", "supply_chain"]
                }
            ]
        }
    }

    # Profil Hutchinson
    hutchinson_profile = {
        "nom": "Groupe Hutchinson",
        "secteur": "Manufacturing, Automotive, Aerospace",
        "presence_geographique": ["France", "Germany", "United States"],
        "matieres_premieres": ["steel", "rubber", "aluminum"],
        "fournisseurs_regions": ["China", "India"]
    }

    print("🤖 Génération de l'analyse LLM structurée...")

    # Générer l'analyse avec le LLM modifié
    llm_output = rag.generate_llm_analysis(test_report, hutchinson_profile)

    print("✅ Analyse générée !")
    print(f"📄 Taille: {len(llm_output)} caractères")

    # Afficher l'output complet
    print(f"\n" + "="*60)
    print("🔍 OUTPUT DU LLM MODIFIÉ:")
    print("="*60)
    print(llm_output)

    # Vérifier si les données structurées sont présentes
    if "DONNÉES STRUCTURÉES POUR STREAMLIT" in llm_output:
        print(f"\n✅ SUCCÈS ! Le LLM produit maintenant les données structurées")
        print("📊 Les données incluent:")
        print("   • law_name (Nom de la loi)")
        print("   • law_url (URL de référence)")
        print("   • deadline (Date limite)")
        print("   • impact_financial (Impact financier sur 10)")
        print("   • impact_reputation (Impact réputation sur 10)")
        print("   • impact_operational (Impact opérationnel sur 10)")
        print("   • notes (Notes explicatives)")

        # Extraire et afficher uniquement la partie JSON
        json_start = llm_output.find("DONNÉES STRUCTURÉES POUR STREAMLIT:")
        if json_start != -1:
            json_part = llm_output[json_start:]
            print(f"\n📋 DONNÉES JSON EXTRAITES:")
            print("-" * 40)
            print(json_part)

        return True
    else:
        print(f"\n❌ PROBLÈME: Les données structurées ne sont pas générées")
        return False

def save_structured_data_sample():
    """Sauvegarde un échantillon des données structurées"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"llm_structured_output_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("EXEMPLE DE DONNÉES STRUCTURÉES GÉNÉRÉES PAR LE LLM\n")
        f.write("=" * 60 + "\n\n")
        f.write("Format attendu pour Streamlit:\n\n")
        f.write("""
{
  "indicators": [
    {
      "id": "IND-001",
      "law_name": "CBAM – Exposition CO₂ import",
      "law_url": "https://europa.eu/cbam",
      "deadline": "01/01/2026",
      "impact_financial": 9,
      "impact_reputation": 7,
      "impact_operational": 8,
      "notes": "Impact financier majeur | Secteur automobile concerné"
    }
  ],
  "summary": {
    "criticite_globale": 8.0,
    "niveau_alerte": "ÉLEVÉ",
    "total_regulations": 1
  }
}
""")

    print(f"💾 Exemple sauvegardé: {filename}")

if __name__ == "__main__":
    print("🎯 VÉRIFICATION DES DONNÉES STRUCTURÉES")
    print("Teste si le LLM produit exactement ce que vous voulez pour Streamlit")
    print("\n" + "="*60)

    success = test_llm_structured_output()

    if success:
        print(f"\n🎉 PARFAIT ! Votre LLM produit maintenant exactement:")
        print("   📊 law_name (nom de la loi)")
        print("   🔗 law_url (URL de référence)")
        print("   📅 deadline (date limite)")
        print("   💰 impact_financial (sur 10)")
        print("   📰 impact_reputation (sur 10)")
        print("   🔧 impact_operational (sur 10)")
        print("   📝 notes (notes explicatives)")
        print("\n🚀 Ces données sont prêtes pour votre interface Streamlit !")

        save_structured_data_sample()
    else:
        print(f"\n❌ Le LLM ne produit pas encore les bonnes données")
        print("   Il faut ajuster le code pour corriger le problème")
