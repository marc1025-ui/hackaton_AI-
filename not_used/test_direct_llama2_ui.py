#!/usr/bin/env python3
"""
Test direct llama2 avec vos données MongoDB - Contournement du système de recherche
"""

from rag_with_llm import RegulatoryRiskRAGWithLLM
from db import db
from datetime import datetime
import json

def test_direct_llama2():
    """Test direct de llama2 en contournant le système de recherche"""

    print("🦙 TEST DIRECT LLAMA2 AVEC VOS DONNÉES")
    print("=" * 60)

    try:
        # Récupérer directement vos données MongoDB
        regulations = list(db.regulations.find().limit(2))  # Limité à 2
        hutchinson = db.hutchinson.find_one()

        if not regulations:
            print("❌ Aucune réglementation en base")
            return False

        if not hutchinson:
            print("❌ Profil Hutchinson non trouvé")
            return False

        print(f"✅ {len(regulations)} réglementations récupérées")
        print(f"✅ Profil Hutchinson récupéré")

        # Afficher les réglementations qui seront analysées
        print(f"\n📋 Réglementations à analyser par llama2:")
        for i, reg in enumerate(regulations, 1):
            deadline = reg.get('date_effet') or reg.get('date_vigueur')
            deadline_str = deadline.strftime('%d/%m/%Y') if deadline else "Non définie"
            print(f"   {i}. {reg.get('nom_loi')}")
            print(f"      📅 Deadline: {deadline_str}")

        # Initialiser le système LLM
        rag = RegulatoryRiskRAGWithLLM("ollama")

        # Créer un rapport simple directement
        fake_report = {
            "detailed_analysis": {
                "high_risk": [
                    {"regulation": regulations[0], "impact_details": ["test"]}
                ],
                "medium_risk": [
                    {"regulation": regulations[1], "impact_details": ["test"]}
                ] if len(regulations) > 1 else []
            }
        }

        # Profil Hutchinson
        hutchinson_profile = {
            "nom": "Groupe Hutchinson",
            "secteur": "Automotive, Aerospace, Industry",
            "presence_geographique": ["France", "Germany", "United States"]
        }

        print(f"\n🤖 Génération analyse llama2 (2 réglementations max)...")

        # Appeler directement llama2
        llm_response = rag.generate_llm_analysis(fake_report, hutchinson_profile)

        print(f"✅ llama2 a répondu !")
        print(f"📄 Taille réponse: {len(str(llm_response))} caractères")

        # Afficher la réponse brute de llama2
        print(f"\n" + "="*70)
        print("🦙 RÉPONSE BRUTE DE LLAMA2:")
        print("="*70)
        print(llm_response)
        print("="*70)

        # Essayer d'extraire les données UI
        try:
            ui_data = rag.extract_ui_data_from_llm_response(llm_response)

            if "error" not in ui_data:
                print(f"\n✅ DONNÉES UI EXTRAITES AVEC SUCCÈS !")

                indicators = ui_data.get('indicators', [])
                print(f"📊 {len(indicators)} indicateurs extraits:")

                for i, ind in enumerate(indicators, 1):
                    print(f"\n{i}. INDICATEUR POUR UI:")
                    print(f"   ✅ law_name: {ind.get('law_name', 'N/A')}")
                    print(f"   ✅ law_url: {ind.get('law_url', '#')}")
                    print(f"   ✅ deadline: {ind.get('deadline', 'N/A')}")
                    print(f"   ✅ impact_financial: {ind.get('impact_financial', 0)}/10")
                    print(f"   ✅ impact_reputation: {ind.get('impact_reputation', 0)}/10")
                    print(f"   ✅ impact_operational: {ind.get('impact_operational', 0)}/10")
                    print(f"   ✅ notes: {ind.get('notes', 'N/A')}")

                # Sauvegarder les données UI
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                ui_filename = f"hutchinson_ui_llama2_{timestamp}.json"

                with open(ui_filename, 'w', encoding='utf-8') as f:
                    json.dump(ui_data, f, indent=2, ensure_ascii=False, default=str)

                print(f"\n💾 Données UI sauvées: {ui_filename}")

            else:
                print(f"❌ Erreur extraction UI: {ui_data['error']}")
                print("📋 Réponse LLM brute (pour debug):")
                print(str(llm_response)[:500] + "...")

        except Exception as e:
            print(f"❌ Erreur extraction: {e}")

        return True

    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 TEST DIRECT LLAMA2 POUR DONNÉES UI")
    print("Test optimisé pour obtenir UNIQUEMENT les données UI que vous voulez")
    print("\n" + "="*60)

    success = test_direct_llama2()

    if success:
        print(f"\n🎉 SUCCÈS ! llama2 génère les données pour votre UI")
        print("📱 Données JSON prêtes pour Streamlit")
    else:
        print(f"\n❌ Problème - vérifiez que llama2 est bien démarré")
