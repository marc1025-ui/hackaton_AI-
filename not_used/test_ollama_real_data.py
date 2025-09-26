#!/usr/bin/env python3
"""
Test du vrai LLM Ollama avec vos données réelles Hutchinson
"""

from rag_with_llm import RegulatoryRiskRAGWithLLM
from db import db
from datetime import datetime
import requests
import time

def test_ollama_with_real_hutchinson_data():
    """Teste Ollama avec vos vraies données MongoDB"""

    print("🦙 TEST OLLAMA LLM AVEC DONNÉES RÉELLES HUTCHINSON")
    print("=" * 70)

    # Étape 1: Vérifier qu'Ollama et llama2 sont prêts
    print("1️⃣ Vérification d'Ollama et llama2...")

    for attempt in range(10):  # Attendre jusqu'à 30 secondes
        try:
            # Vérifier qu'Ollama répond
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models_data = response.json()
                models = [m.get('name', 'N/A') for m in models_data.get('models', [])]

                if 'llama2' in str(models) or any('llama2' in str(m) for m in models):
                    print("✅ Ollama et llama2 sont prêts !")
                    print(f"📋 Modèles disponibles: {models}")
                    break
                else:
                    print(f"⏳ Tentative {attempt + 1}/10 - llama2 en cours de téléchargement...")
                    print(f"   Modèles actuels: {models}")
                    time.sleep(3)
            else:
                print(f"⚠️ Ollama répond avec erreur {response.status_code}")
                time.sleep(3)
        except requests.exceptions.ConnectionError:
            print(f"⏳ Tentative {attempt + 1}/10 - Ollama en cours de démarrage...")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            time.sleep(3)
    else:
        print("❌ Timeout - llama2 n'est pas encore prêt")
        print("💡 Vérifiez manuellement avec: ollama list")
        return False

    # Étape 2: Récupérer vos vraies données
    print(f"\n2️⃣ Récupération de vos données réelles...")

    try:
        regulations = list(db.regulations.find())
        hutchinson = db.hutchinson.find_one()

        if not regulations:
            print("❌ Aucune réglementation trouvée dans MongoDB")
            return False

        if not hutchinson:
            print("❌ Profil Hutchinson non trouvé dans MongoDB")
            return False

        print(f"✅ {len(regulations)} réglementations récupérées")
        print(f"✅ Profil Hutchinson récupéré")

        # Afficher les réglementations qui seront analysées
        print(f"\n📋 Réglementations à analyser par llama2:")
        for i, reg in enumerate(regulations, 1):
            print(f"   {i}. {reg.get('nom_loi', 'Nom non défini')}")

    except Exception as e:
        print(f"❌ Erreur récupération données: {e}")
        return False

    # Étape 3: Initialiser le système avec Ollama
    print(f"\n3️⃣ Initialisation du système RAG avec Ollama...")

    try:
        rag_ollama = RegulatoryRiskRAGWithLLM("ollama")  # Mode Ollama
        print("✅ Système RAG + Ollama initialisé")
    except Exception as e:
        print(f"❌ Erreur initialisation RAG: {e}")
        return False

    # Étape 4: Préparer les données pour llama2
    print(f"\n4️⃣ Préparation des données pour llama2...")

    # Calculer les scores d'impact avec vos données
    high_risks = []
    medium_risks = []

    for reg in regulations:
        # Score d'impact basé sur Hutchinson
        impact_score = calculate_hutchinson_impact_score(reg, hutchinson)

        risk_entry = {
            "regulation": reg,
            "impact_details": [f"impact_score:{impact_score:.3f}"]
        }

        if impact_score >= 0.5:
            high_risks.append(risk_entry)
        elif impact_score >= 0.3:
            medium_risks.append(risk_entry)

    # Créer le rapport pour llama2
    real_report = {
        "detailed_analysis": {
            "high_risk": high_risks,
            "medium_risk": medium_risks
        }
    }

    # Profil Hutchinson pour llama2
    hutchinson_profile = {
        "nom": hutchinson.get('company_info', {}).get('name', 'Hutchinson'),
        "secteur": ', '.join(hutchinson.get('company_info', {}).get('sectors', [])),
        "presence_geographique": hutchinson.get('geographical_presence', [])[:5],
        "matieres_premieres": hutchinson.get('typical_materials', [])[:5],
        "fournisseurs_regions": hutchinson.get('geographical_presence', [])[:3]
    }

    print(f"✅ Données préparées:")
    print(f"   • Risques élevés: {len(high_risks)}")
    print(f"   • Risques moyens: {len(medium_risks)}")
    print(f"   • Profil: {hutchinson_profile['nom']}")

    # Étape 5: Génération avec llama2
    print(f"\n5️⃣ 🦙 GÉNÉRATION AVEC LLAMA2 LLM...")
    print("   (Cela peut prendre 30-120 secondes selon la complexité...)")

    try:
        start_time = time.time()

        # Appel du vrai LLM llama2
        llm_analysis = rag_ollama.generate_llm_analysis(real_report, hutchinson_profile)

        end_time = time.time()
        generation_time = end_time - start_time

        print(f"⏱️ Temps de génération llama2: {generation_time:.1f} secondes")

        if "Erreur" in str(llm_analysis):
            print(f"❌ Erreur llama2: {llm_analysis}")
            return False

        print(f"✅ SUCCÈS ! llama2 a généré l'analyse")
        print(f"📄 Taille de la réponse: {len(str(llm_analysis))} caractères")

        # Afficher l'analyse de llama2
        print(f"\n" + "="*80)
        print("🦙 ANALYSE GÉNÉRÉE PAR LLAMA2 LLM AVEC VOS DONNÉES RÉELLES:")
        print("="*80)
        print(llm_analysis)
        print("="*80)

        # Sauvegarder l'analyse
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"hutchinson_llama2_real_analysis_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ANALYSE HUTCHINSON PAR LLAMA2 LLM - DONNÉES RÉELLES\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Modèle LLM: llama2\n")
            f.write(f"Temps de génération: {generation_time:.1f} secondes\n")
            f.write(f"Réglementations analysées: {len(regulations)}\n")
            f.write(f"Risques élevés détectés: {len(high_risks)}\n")
            f.write(f"Risques moyens détectés: {len(medium_risks)}\n\n")
            f.write("PROFIL HUTCHINSON:\n")
            f.write(f"Nom: {hutchinson_profile['nom']}\n")
            f.write(f"Secteurs: {hutchinson_profile['secteur']}\n")
            f.write(f"Géographie: {hutchinson_profile['presence_geographique']}\n\n")
            f.write("ANALYSE LLAMA2:\n")
            f.write("-" * 60 + "\n")
            f.write(str(llm_analysis))

        print(f"\n💾 Analyse llama2 sauvée: {filename}")

        # Comparer avec l'analyse par règles
        print(f"\n6️⃣ Comparaison avec l'analyse par règles...")

        rag_rules = RegulatoryRiskRAGWithLLM("rules")
        rules_analysis = rag_rules.generate_llm_analysis(real_report, hutchinson_profile)

        print(f"📊 Comparaison:")
        print(f"   • llama2 LLM: {len(str(llm_analysis))} caractères")
        print(f"   • Système règles: {len(str(rules_analysis))} caractères")

        return True

    except Exception as e:
        print(f"❌ Erreur génération llama2: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_hutchinson_impact_score(regulation, hutchinson_profile):
    """Calcule le score d'impact pour Hutchinson"""
    score = 0.0

    # Score géographique
    hutch_geo = hutchinson_profile.get('geographical_presence', [])
    reg_countries = regulation.get('pays_concernes', [])
    if hutch_geo and reg_countries:
        geo_matches = len(set(hutch_geo) & set(reg_countries))
        score += min(0.4, (geo_matches / len(reg_countries)) * 0.4)

    # Score sectoriel
    hutch_sectors = [s.lower() for s in hutchinson_profile.get('company_info', {}).get('sectors', [])]
    reg_sectors = [s.lower() for s in regulation.get('secteurs', [])]
    if hutch_sectors and reg_sectors:
        sector_matches = len(set(hutch_sectors) & set(reg_sectors))
        score += min(0.35, (sector_matches / len(reg_sectors)) * 0.35)

    # Score mots-clés
    reg_text = regulation.get('texte', '').lower()
    hutch_keywords = ['sealing', 'automotive', 'aerospace', 'rubber', 'steel', 'vibration']
    keyword_matches = sum(1 for keyword in hutch_keywords if keyword in reg_text)
    score += min(0.25, (keyword_matches / len(hutch_keywords)) * 0.25)

    return min(1.0, score)

if __name__ == "__main__":
    print("🚀 TEST DU VRAI LLM LLAMA2 AVEC HUTCHINSON")
    print("Ce test utilise le modèle llama2 que vous venez d'installer")
    print("pour analyser vos vraies données réglementaires.")
    print("\n" + "="*70)

    success = test_ollama_with_real_hutchinson_data()

    if success:
        print(f"\n🎉 SUCCÈS COMPLET !")
        print("🦙 llama2 LLM fonctionne parfaitement avec vos données")
        print("🎯 Votre système utilise maintenant un VRAI LLM pour l'analyse")
        print("\n💡 Pour utiliser llama2 dans vos analyses:")
        print("   rag = RegulatoryRiskRAGWithLLM('ollama')")
        print("   # Le système utilisera automatiquement llama2")
    else:
        print(f"\n❌ PROBLÈME DÉTECTÉ")
        print("💡 Vérifications possibles:")
        print("   • ollama list (vérifier que llama2 est téléchargé)")
        print("   • ollama run llama2 (tester llama2 manuellement)")
        print("   • curl http://localhost:11434/api/tags (vérifier Ollama)")
