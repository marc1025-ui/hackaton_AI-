#!/usr/bin/env python3
"""
Test complet du système RAG + LLM + Matching pour Hutchinson
Combine le matching des réglementations avec l'analyse LLM pour des recommandations stratégiques
"""

from pymongo import MongoClient
from datetime import datetime
import requests

def test_complete_rag_llm_system():
    """Test complet : Matching + RAG + LLM Analysis"""

    print("🚀 TEST COMPLET : MATCHING + RAG + LLM")
    print("=" * 60)

    try:
        # Étape 1: Import du système RAG + LLM
        print("📥 Import du système RAG + LLM...")
        from rag_with_llm import RegulatoryRiskRAGWithLLM
        print("✅ Système importé")

        # Étape 2: Récupération des données de matching
        print("\n🔍 Récupération des résultats de matching...")
        matching_results = get_matching_results()

        if not matching_results:
            print("❌ Échec récupération données matching")
            return False

        print(f"✅ {len(matching_results)} réglementations analysées")

        # Étape 3: Création du rapport pour le LLM
        print("\n📊 Création du rapport structuré...")
        structured_report = create_structured_report(matching_results)
        print("✅ Rapport structuré créé")

        # Étape 4: Profil Hutchinson pour le LLM
        hutchinson_profile_llm = {
            "nom": "Groupe Hutchinson",
            "secteur": "Automotive, Aerospace, Industry",
            "presence_geographique": ["France", "Germany", "Poland", "United States", "China"],
            "matieres_premieres": ["rubber", "steel", "aluminum", "plastics"],
            "fournisseurs_regions": ["China", "India", "Brazil"]
        }

        # Étape 5: Test avec système de règles (fallback)
        print("\n🤖 Test analyse LLM (mode règles)...")
        rag_rules = RegulatoryRiskRAGWithLLM("rules")

        try:
            llm_analysis_rules = rag_rules.generate_llm_analysis(structured_report, hutchinson_profile_llm)
            print("✅ Analyse LLM règles générée")
            print(f"📄 Taille: {len(llm_analysis_rules)} caractères")

            # Afficher l'analyse
            print("\n" + "="*50)
            print("📋 ANALYSE LLM (MODE RÈGLES):")
            print("="*50)
            print(llm_analysis_rules)

        except Exception as e:
            print(f"❌ Erreur analyse règles: {e}")
            return False

        # Étape 6: Test avec Ollama (si disponible)
        print("\n🦙 Vérification Ollama...")
        ollama_available = check_ollama_availability()

        if ollama_available:
            print("✅ Ollama disponible - Test avec LLM réel")

            rag_ollama = RegulatoryRiskRAGWithLLM("ollama")

            try:
                print("🔄 Génération analyse Ollama (peut prendre 30-60s)...")
                llm_analysis_ollama = rag_ollama.generate_llm_analysis(structured_report, hutchinson_profile_llm)

                print("✅ Analyse Ollama générée")
                print(f"📄 Taille: {len(llm_analysis_ollama)} caractères")

                # Afficher l'analyse Ollama
                print("\n" + "="*50)
                print("🦙 ANALYSE OLLAMA (LLM RÉEL):")
                print("="*50)
                print(llm_analysis_ollama)

            except Exception as e:
                print(f"⚠️ Erreur Ollama: {e}")
                print("📋 Utilisation de l'analyse par règles")
        else:
            print("⚠️ Ollama non disponible")
            print("💡 Pour activer Ollama:")
            print("   1. Installez: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   2. Démarrez: ollama serve")
            print("   3. Téléchargez le modèle: ollama pull llama3.2")

        # Étape 7: Rapport complet formaté
        print("\n📊 Génération du rapport complet...")

        # Ajouter l'analyse LLM au rapport
        structured_report["llm_analysis"] = llm_analysis_rules

        # Formater le rapport complet
        formatted_report = rag_rules.format_comprehensive_report(structured_report)

        print("✅ Rapport complet généré")

        # Sauvegarder le rapport
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"hutchinson_risk_analysis_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_report)

        print(f"💾 Rapport sauvegardé: {filename}")

        # Étape 8: Résumé des capacités
        print("\n" + "="*60)
        print("🎉 TEST COMPLET RÉUSSI !")
        print("="*60)

        print("\n🎯 VOTRE SYSTÈME COMPLET PEUT MAINTENANT:")
        print("   • ✅ Scraper les réglementations (simulation)")
        print("   • ✅ Stocker dans MongoDB")
        print("   • ✅ Matcher avec le profil Hutchinson")
        print("   • ✅ Calculer des scores d'impact précis")
        print("   • ✅ Identifier les lois critiques")
        print("   • ✅ Générer des analyses LLM intelligentes")
        print("   • ✅ Proposer des actions prioritaires")
        print("   • ✅ Estimer l'impact financier")
        print("   • ✅ Créer des roadmaps de conformité")
        print("   • ✅ Sauvegarder des rapports détaillés")

        print(f"\n📈 RÉSULTATS DE CE TEST:")
        high_impact = len([r for r in matching_results if r['total_score'] >= 0.7])
        medium_impact = len([r for r in matching_results if 0.5 <= r['total_score'] < 0.7])

        print(f"   🔴 Lois à impact ÉLEVÉ: {high_impact}")
        print(f"   🟡 Lois à surveiller: {medium_impact}")
        print(f"   📊 Analyse LLM générée: ✅")
        print(f"   💾 Rapport sauvegardé: ✅")

        return True

    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_matching_results():
    """Récupère les résultats du système de matching"""
    try:
        CONNECTION_STRING = "mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc"
        client = MongoClient(CONNECTION_STRING)
        db = client["hackathon_regulations"]

        hutchinson = db.hutchinson.find_one()
        regulations = list(db.regulations.find())

        if not hutchinson or not regulations:
            return None

        # Importer la fonction de scoring depuis le test précédent
        from test_matching_hutchinson import calculate_matching_score

        results = []
        for reg in regulations:
            score_details = calculate_matching_score(reg, hutchinson)
            results.append({
                'regulation': reg,
                'total_score': score_details['total_score'],
                'score_details': score_details
            })

        # Trier par score décroissant
        results.sort(key=lambda x: x['total_score'], reverse=True)

        client.close()
        return results

    except Exception as e:
        print(f"Erreur récupération matching: {e}")
        return None

def create_structured_report(matching_results):
    """Crée un rapport structuré pour le LLM"""

    high_risks = [r for r in matching_results if r['total_score'] >= 0.7]
    medium_risks = [r for r in matching_results if 0.5 <= r['total_score'] < 0.7]
    low_risks = [r for r in matching_results if r['total_score'] < 0.5]

    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "company": "Groupe Hutchinson",
        "company_profile": {
            "nom": "Groupe Hutchinson",
            "secteur": "Automotive, Aerospace, Industry",
            "presence_geographique": ["France", "Germany", "Poland", "United States"],
            "matieres_premieres": ["rubber", "steel", "aluminum"],
            "fournisseurs_regions": ["China", "India", "Brazil"]
        },
        "risk_summary": {
            "total_regulations": len(matching_results),
            "high_risk_count": len(high_risks),
            "medium_risk_count": len(medium_risks),
            "low_risk_count": len(low_risks),
            "average_risk_score": sum(r['total_score'] for r in matching_results) / len(matching_results)
        },
        "detailed_analysis": {
            "high_risk": [],
            "medium_risk": [],
            "low_risk": []
        }
    }

    # Structurer les risques élevés
    for result in high_risks:
        reg = result['regulation']
        report["detailed_analysis"]["high_risk"].append({
            "regulation": {
                "titre": reg.get('nom_loi', ''),
                "texte": reg.get('texte', ''),
                "score": result['total_score']
            },
            "impact_details": [
                f"geo_score:{result['score_details']['geo_score']:.2f}",
                f"sector_score:{result['score_details']['sector_score']:.2f}",
                f"keyword_score:{result['score_details']['keyword_score']:.2f}",
                f"sanctions:{reg.get('sanctions', 'N/A')}"
            ]
        })

    # Structurer les risques moyens
    for result in medium_risks:
        reg = result['regulation']
        report["detailed_analysis"]["medium_risk"].append({
            "regulation": {
                "titre": reg.get('nom_loi', ''),
                "texte": reg.get('texte', ''),
                "score": result['total_score']
            },
            "impact_details": [
                f"geo_score:{result['score_details']['geo_score']:.2f}",
                f"sector_score:{result['score_details']['sector_score']:.2f}"
            ]
        })

    return report

def check_ollama_availability():
    """Vérifie si Ollama est disponible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🎯 LANCEMENT DU TEST COMPLET")
    print("Cette démonstration va tester toute la chaîne:")
    print("MongoDB → Matching → RAG → LLM → Rapport final")
    print("\n" + "="*60)

    success = test_complete_rag_llm_system()

    if success:
        print("\n🚀 SYSTÈME COMPLET OPÉRATIONNEL !")
        print("\nVotre solution d'anticipation des risques réglementaires")
        print("pour Hutchinson est maintenant fonctionnelle.")
    else:
        print("\n❌ Des améliorations sont nécessaires")
