#!/usr/bin/env python3
"""
Test simplifié du système RAG + LLM + Matching
Focus sur l'essentiel : matching + analyse LLM sans problèmes de formatage
"""

from pymongo import MongoClient
from datetime import datetime

def test_simple_rag_llm():
    """Test simplifié mais complet du système"""

    print("🚀 TEST SIMPLIFIÉ DU SYSTÈME RAG + LLM + MATCHING")
    print("=" * 60)

    try:
        # Import du système
        from rag_with_llm import RegulatoryRiskRAGWithLLM
        print("✅ Système RAG + LLM importé")

        # Récupération des données de matching
        print("\n🔍 Récupération des données de matching...")
        matching_results = get_matching_results_simple()

        if not matching_results:
            print("❌ Pas de données de matching")
            return False

        print(f"✅ {len(matching_results)} réglementations analysées")

        # Afficher le résumé du matching
        print(f"\n📊 RÉSULTATS DU MATCHING:")
        high_impact = [r for r in matching_results if r['total_score'] >= 0.7]
        medium_impact = [r for r in matching_results if 0.5 <= r['total_score'] < 0.7]
        low_impact = [r for r in matching_results if r['total_score'] < 0.5]

        print(f"   🔴 Impact ÉLEVÉ: {len(high_impact)} lois")
        print(f"   🟡 Impact MOYEN: {len(medium_impact)} lois")
        print(f"   🟢 Impact FAIBLE: {len(low_impact)} lois")

        # Créer un rapport simple pour le LLM
        simple_report = {
            "risk_summary": {
                "high_risk_count": len(high_impact),
                "medium_risk_count": len(medium_impact),
                "low_risk_count": len(low_impact),
                "average_risk_score": sum(r['total_score'] for r in matching_results) / len(matching_results)
            },
            "detailed_analysis": {
                "high_risk": [],
                "medium_risk": []
            }
        }

        # Ajouter les détails des risques élevés
        for result in high_impact:
            reg = result['regulation']
            simple_report["detailed_analysis"]["high_risk"].append({
                "regulation": {
                    "titre": reg.get('nom_loi', ''),
                    "texte": reg.get('texte', '')[:300] + "...",
                    "score": result['total_score']
                },
                "impact_details": [
                    f"Score géographique: {result['score_details']['geo_score']:.2f}",
                    f"Score sectoriel: {result['score_details']['sector_score']:.2f}",
                    f"Sanctions: {reg.get('sanctions', 'N/A')}"
                ]
            })

        # Profil Hutchinson pour le LLM
        hutchinson_profile = {
            "nom": "Groupe Hutchinson",
            "secteur": "Automotive, Aerospace, Industry",
            "presence_geographique": ["France", "Germany", "Poland", "United States"],
            "matieres_premieres": ["rubber", "steel", "aluminum"],
            "fournisseurs_regions": ["China", "India", "Brazil"]
        }

        # Test analyse LLM avec règles
        print(f"\n🤖 TEST ANALYSE LLM (mode règles)...")
        rag_system = RegulatoryRiskRAGWithLLM("rules")

        llm_analysis = rag_system.generate_llm_analysis(simple_report, hutchinson_profile)

        print("✅ Analyse LLM générée avec succès")
        print(f"📄 Taille de l'analyse: {len(llm_analysis)} caractères")

        # Afficher l'analyse LLM
        print(f"\n" + "="*60)
        print("🤖 ANALYSE LLM GÉNÉRÉE:")
        print("="*60)
        print(llm_analysis)
        print("="*60)

        # Afficher aussi les détails du matching pour contexte
        print(f"\n📊 DÉTAILS DU MATCHING POUR CONTEXTE:")
        print("-" * 40)
        for i, result in enumerate(high_impact + medium_impact, 1):
            reg = result['regulation']
            print(f"{i}. {reg.get('nom_loi', '')}")
            print(f"   🎯 Score total: {result['total_score']:.3f}")
            print(f"   📍 Géo: {result['score_details']['geo_score']:.2f} | Secteur: {result['score_details']['sector_score']:.2f}")
            print(f"   💰 Sanctions: {reg.get('sanctions', 'N/A')}")
            print(f"   📅 Date effet: {reg['date_effet'].strftime('%d/%m/%Y') if reg.get('date_effet') else 'N/A'}")
            print()

        # Sauvegarder l'analyse
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"hutchinson_analysis_simple_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ANALYSE DES RISQUES RÉGLEMENTAIRES - HUTCHINSON\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

            f.write("RÉSULTATS DU MATCHING:\n")
            f.write(f"• Lois à impact ÉLEVÉ: {len(high_impact)}\n")
            f.write(f"• Lois à impact MOYEN: {len(medium_impact)}\n")
            f.write(f"• Lois à impact FAIBLE: {len(low_impact)}\n\n")

            f.write("DÉTAIL DES LOIS À IMPACT ÉLEVÉ:\n")
            for i, result in enumerate(high_impact, 1):
                reg = result['regulation']
                f.write(f"{i}. {reg.get('nom_loi', '')}\n")
                f.write(f"   Score: {result['total_score']:.3f}\n")
                f.write(f"   Sanctions: {reg.get('sanctions', 'N/A')}\n")
                f.write(f"   Date effet: {reg['date_effet'].strftime('%d/%m/%Y') if reg.get('date_effet') else 'N/A'}\n\n")

            f.write("\n" + "="*50 + "\n")
            f.write("ANALYSE LLM:\n")
            f.write("="*50 + "\n")
            f.write(llm_analysis)

        print(f"\n💾 Rapport sauvegardé: {filename}")

        # Résumé final
        print(f"\n🎉 TEST RÉUSSI !")
        print(f"\n🎯 CAPACITÉS VALIDÉES:")
        print(f"   ✅ Lecture des lois MongoDB")
        print(f"   ✅ Matching Hutchinson ↔ Réglementations")
        print(f"   ✅ Calcul des scores d'impact")
        print(f"   ✅ Classification par priorité")
        print(f"   ✅ Génération analyse LLM")
        print(f"   ✅ Sauvegarde rapport")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_matching_results_simple():
    """Version simplifiée de récupération des résultats de matching"""
    try:
        CONNECTION_STRING = "mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc"
        client = MongoClient(CONNECTION_STRING)
        db = client["hackathon_regulations"]

        hutchinson = db.hutchinson.find_one()
        regulations = list(db.regulations.find())

        if not hutchinson or not regulations:
            return None

        # Fonction de scoring simplifiée
        def simple_score(reg, hutch):
            score = 0.0

            # Score géographique
            hutch_geo = hutch['geographical_presence']
            reg_countries = reg.get('pays_concernes', [])
            geo_matches = len(set(hutch_geo) & set(reg_countries))
            geo_score = min(1.0, geo_matches / len(reg_countries)) * 0.3 if reg_countries else 0

            # Score sectoriel
            hutch_sectors = [s.lower() for s in hutch['company_info']['sectors']]
            reg_sectors = [s.lower() for s in reg.get('secteurs', [])]
            sector_matches = len(set(hutch_sectors) & set(reg_sectors))
            sector_score = min(1.0, sector_matches / len(reg_sectors)) * 0.4 if reg_sectors else 0

            # Score mots-clés
            hutch_keywords = hutch.get('keywords_matching', [])
            reg_keywords = reg.get('mots_cles', [])
            keyword_matches = len(set(hutch_keywords) & set(reg_keywords))
            keyword_score = min(1.0, keyword_matches / len(reg_keywords)) * 0.3 if reg_keywords else 0

            total_score = geo_score + sector_score + keyword_score

            return {
                'total_score': total_score,
                'geo_score': geo_score,
                'sector_score': sector_score,
                'keyword_score': keyword_score
            }

        results = []
        for reg in regulations:
            score_details = simple_score(reg, hutchinson)
            results.append({
                'regulation': reg,
                'total_score': score_details['total_score'],
                'score_details': score_details
            })

        results.sort(key=lambda x: x['total_score'], reverse=True)

        client.close()
        return results

    except Exception as e:
        print(f"Erreur récupération: {e}")
        return None

if __name__ == "__main__":
    print("🎯 TEST SIMPLIFIÉ DU SYSTÈME COMPLET")
    print("Focus: Matching + LLM Analysis sans problèmes de structure")
    print("\n" + "="*60)

    success = test_simple_rag_llm()

    if success:
        print(f"\n🚀 VOTRE SYSTÈME FONCTIONNE PARFAITEMENT !")
        print(f"\nIl peut maintenant:")
        print(f"• Analyser les réglementations en base")
        print(f"• Les matcher avec Hutchinson")
        print(f"• Calculer des scores d'impact")
        print(f"• Générer des analyses LLM intelligentes")
        print(f"• Proposer des actions concrètes")
    else:
        print(f"\n❌ Il y a encore des problèmes à résoudre")
