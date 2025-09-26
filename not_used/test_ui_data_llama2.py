#!/usr/bin/env python3
"""
Test du système modifié avec llama2 LLM pour données UI
"""

from rag_with_llm import RegulatoryRiskRAGWithLLM
from db import db

def test_ui_data_with_llama2():
    """Teste la nouvelle méthode get_ui_ready_data() avec llama2"""

    print("🦙 TEST DONNÉES UI AVEC LLAMA2 LLM")
    print("=" * 50)

    try:
        # Récupérer le profil Hutchinson réel
        hutchinson = db.hutchinson.find_one()

        if not hutchinson:
            print("❌ Profil Hutchinson non trouvé")
            return False

        # Profil pour le LLM
        hutchinson_profile = {
            "nom": hutchinson.get('company_info', {}).get('name', 'Hutchinson'),
            "secteur": ', '.join(hutchinson.get('company_info', {}).get('sectors', [])),
            "presence_geographique": hutchinson.get('geographical_presence', [])[:3],
            "matieres_premieres": hutchinson.get('typical_materials', [])[:3],
            "fournisseurs_regions": hutchinson.get('geographical_presence', [])[:3]
        }

        print(f"✅ Profil Hutchinson: {hutchinson_profile['nom']}")
        print(f"📊 Secteurs: {hutchinson_profile['secteur']}")

        # Initialiser avec Ollama
        rag = RegulatoryRiskRAGWithLLM("ollama")

        print(f"\n🦙 Génération des données UI avec llama2...")
        print("   (Maximum 2 réglementations, ~30-60s)")

        # Utiliser la nouvelle méthode
        ui_data = rag.get_ui_ready_data(hutchinson_profile)

        print("✅ Données UI générées par llama2 !")

        # Afficher les résultats
        if "error" in ui_data:
            print(f"❌ Erreur: {ui_data['error']}")
            return False

        print(f"\n📊 MÉTADONNÉES:")
        metadata = ui_data.get('metadata', {})
        print(f"   • Entreprise: {metadata.get('company_name')}")
        print(f"   • Date: {metadata.get('analysis_date')}")
        print(f"   • Indicateurs: {metadata.get('total_indicators')}")
        print(f"   • Modèle: {metadata.get('model')}")

        print(f"\n📋 DONNÉES POUR VOTRE UI:")
        print("=" * 40)

        indicators = ui_data.get('indicators', [])
        for i, indicator in enumerate(indicators, 1):
            print(f"{i}. {indicator.get('law_name', 'N/A')}")
            print(f"   🔗 URL: {indicator.get('law_url', '#')}")
            print(f"   📅 Deadline: {indicator.get('deadline', 'N/A')}")
            print(f"   💰 Impact financier: {indicator.get('impact_financial', 0)}/10")
            print(f"   📰 Impact réputation: {indicator.get('impact_reputation', 0)}/10")
            print(f"   🔧 Impact opérationnel: {indicator.get('impact_operational', 0)}/10")
            print(f"   📝 Notes: {indicator.get('notes', 'N/A')}")
            print()

        # Sauvegarder pour votre UI
        import json
        from datetime import datetime

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ui_filename = f"hutchinson_ui_data_{timestamp}.json"

        with open(ui_filename, 'w', encoding='utf-8') as f:
            json.dump(ui_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"💾 Données UI sauvées: {ui_filename}")
        print("📱 Ces données sont prêtes pour votre interface Streamlit !")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 TEST DES DONNÉES UI AVEC LLAMA2")
    print("Ce test utilise llama2 pour générer UNIQUEMENT les données")
    print("que vous voulez afficher dans votre interface utilisateur.")
    print("\n" + "="*60)

    success = test_ui_data_with_llama2()

    if success:
        print(f"\n🎉 SUCCÈS ! Votre système génère maintenant:")
        print("   ✅ law_name - Nom de la loi")
        print("   ✅ law_url - URL de référence")
        print("   ✅ deadline - Date limite")
        print("   ✅ impact_financial - Impact financier (sur 10)")
        print("   ✅ impact_reputation - Impact réputation (sur 10)")
        print("   ✅ impact_operational - Impact opérationnel (sur 10)")
        print("   ✅ notes - Notes explicatives")
        print("\n🚀 Données JSON prêtes pour Streamlit UI !")
    else:
        print(f"\n❌ Problème détecté - vérifiez llama2")
