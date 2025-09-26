#!/usr/bin/env python3
"""
Test avec les données RÉELLES de la collection MongoDB
Analyse les vraies réglementations stockées dans votre base de données
"""

from pymongo import MongoClient
from datetime import datetime

def test_with_real_data():
    """Test avec les données réelles de MongoDB"""

    print("🚀 TEST AVEC LES DONNÉES RÉELLES DE LA COLLECTION")
    print("=" * 60)

    try:
        # Connexion à la vraie base MongoDB
        CONNECTION_STRING = "mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc"
        client = MongoClient(CONNECTION_STRING)
        db = client["hackathon_regulations"]

        print("✅ Connexion MongoDB établie")

        # Vérifier les collections disponibles
        collections = db.list_collection_names()
        print(f"📂 Collections disponibles: {collections}")

        # Récupérer toutes les réglementations réelles
        print("\n📚 Récupération des réglementations réelles...")
        regulations = list(db.regulations.find())

        if not regulations:
            print("❌ Aucune réglementation trouvée dans la collection")
            print("💡 Assurez-vous d'avoir d'abord exécuté mongodb_setup.py")
            return False

        print(f"✅ {len(regulations)} réglementations trouvées dans la base")

        # Afficher les réglementations disponibles
        print(f"\n📋 RÉGLEMENTATIONS DANS LA BASE:")
        print("-" * 50)
        for i, reg in enumerate(regulations, 1):
            print(f"{i}. {reg.get('nom_loi', 'Nom non disponible')}")
            print(f"   ID: {reg.get('id_loi', 'N/A')}")
            print(f"   Type: {reg.get('type', 'N/A')}")
            print(f"   Pays: {reg.get('pays_concernes', 'N/A')}")
            print(f"   Date effet: {reg.get('date_effet', 'N/A')}")
            print()

        # Récupérer le profil Hutchinson réel
        print("🏢 Récupération du profil Hutchinson...")
        hutchinson = db.hutchinson.find_one()

        if not hutchinson:
            print("❌ Profil Hutchinson non trouvé")
            return False

        print("✅ Profil Hutchinson récupéré")
        print(f"   Secteurs: {hutchinson.get('company_info', {}).get('sectors', 'N/A')}")
        print(f"   Géographie: {len(hutchinson.get('geographical_presence', []))} pays")

        # Import du système RAG + LLM
        from rag_with_llm import RegulatoryRiskRAGWithLLM
        print("\n🤖 Initialisation du système RAG + LLM...")

        # Initialiser en mode règles
        rag_system = RegulatoryRiskRAGWithLLM("rules")
        print("✅ Système initialisé")

        # Calculer les scores de matching avec les données réelles
        print("\n🔍 ANALYSE DE MATCHING AVEC DONNÉES RÉELLES:")
        print("=" * 50)

        matching_results = []

        for reg in regulations:
            score_details = calculate_real_matching_score(reg, hutchinson)
            matching_results.append({
                'regulation': reg,
                'total_score': score_details['total_score'],
                'score_details': score_details
            })

        # Trier par score décroissant
        matching_results.sort(key=lambda x: x['total_score'], reverse=True)

        # Classifier par niveaux d'impact
        high_impact = [r for r in matching_results if r['total_score'] >= 0.7]
        medium_impact = [r for r in matching_results if 0.5 <= r['total_score'] < 0.7]
        low_impact = [r for r in matching_results if 0.3 <= r['total_score'] < 0.5]
        negligible = [r for r in matching_results if r['total_score'] < 0.3]

        # Afficher les résultats du matching
        print(f"📊 RÉSULTATS DU MATCHING:")
        print(f"   🔴 Impact TRÈS ÉLEVÉ: {len(high_impact)} lois (score ≥ 0.7)")
        print(f"   🟡 Impact MOYEN: {len(medium_impact)} lois (0.5 ≤ score < 0.7)")
        print(f"   🟠 Impact FAIBLE: {len(low_impact)} lois (0.3 ≤ score < 0.5)")
        print(f"   🟢 Impact NÉGLIGEABLE: {len(negligible)} lois (score < 0.3)")

        # Détailler les résultats par catégorie
        if high_impact:
            print(f"\n🔴 LOIS À IMPACT TRÈS ÉLEVÉ:")
            for i, result in enumerate(high_impact, 1):
                reg = result['regulation']
                print(f"   {i}. {reg.get('nom_loi', '')}")
                print(f"      🎯 Score: {result['total_score']:.3f}")
                print(f"      📍 Détail: Géo={result['score_details']['geo_score']:.2f} | "
                      f"Secteur={result['score_details']['sector_score']:.2f} | "
                      f"Keywords={result['score_details']['keyword_score']:.2f}")
                print(f"      📅 Date effet: {reg.get('date_effet', 'N/A')}")
                print(f"      💰 Sanctions: {reg.get('sanctions', 'Non spécifiées')}")
                print()

        if medium_impact:
            print(f"🟡 LOIS À IMPACT MOYEN:")
            for i, result in enumerate(medium_impact, 1):
                reg = result['regulation']
                print(f"   {i}. {reg.get('nom_loi', '')}")
                print(f"      🎯 Score: {result['total_score']:.3f}")
                print(f"      📅 Date effet: {reg.get('date_effet', 'N/A')}")
                print()

        # Créer un rapport pour l'analyse LLM
        if high_impact or medium_impact:
            print(f"\n🤖 GÉNÉRATION DE L'ANALYSE LLM...")

            # Préparer le rapport pour le LLM
            llm_report = {
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
                llm_report["detailed_analysis"]["high_risk"].append({
                    "regulation": {
                        "titre": reg.get('nom_loi', ''),
                        "texte": str(reg.get('texte', ''))[:500] + "...",
                        "score": result['total_score']
                    },
                    "impact_details": [
                        f"Score géographique: {result['score_details']['geo_score']:.2f}",
                        f"Score sectoriel: {result['score_details']['sector_score']:.2f}",
                        f"Date effet: {reg.get('date_effet', 'N/A')}",
                        f"Sanctions: {reg.get('sanctions', 'Non spécifiées')}"
                    ]
                })

            # Profil Hutchinson pour le LLM
            hutch_profile_llm = {
                "nom": hutchinson.get('company_info', {}).get('name', 'Hutchinson'),
                "secteur": ', '.join(hutchinson.get('company_info', {}).get('sectors', [])),
                "presence_geographique": hutchinson.get('geographical_presence', [])[:5],  # Limiter pour le prompt
                "matieres_premieres": hutchinson.get('typical_materials', [])[:5],
                "fournisseurs_regions": hutchinson.get('geographical_presence', [])[:3]
            }

            # Générer l'analyse LLM
            llm_analysis = rag_system.generate_llm_analysis(llm_report, hutch_profile_llm)

            print("✅ Analyse LLM générée")
            print(f"📄 Taille: {len(llm_analysis)} caractères")

            # Afficher l'analyse LLM
            print(f"\n" + "="*60)
            print("🤖 ANALYSE LLM AVEC DONNÉES RÉELLES:")
            print("="*60)
            print(llm_analysis)
            print("="*60)

            # Sauvegarder le rapport avec données réelles
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hutchinson_real_data_analysis_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ANALYSE DES RISQUES RÉGLEMENTAIRES - HUTCHINSON (DONNÉES RÉELLES)\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Nombre de réglementations analysées: {len(regulations)}\n\n")

                f.write("RÉSULTATS DU MATCHING:\n")
                f.write(f"• Lois à impact TRÈS ÉLEVÉ: {len(high_impact)}\n")
                f.write(f"• Lois à impact MOYEN: {len(medium_impact)}\n")
                f.write(f"• Lois à impact FAIBLE: {len(low_impact)}\n")
                f.write(f"• Lois négligeables: {len(negligible)}\n\n")

                if high_impact:
                    f.write("DÉTAIL DES LOIS À IMPACT TRÈS ÉLEVÉ:\n")
                    for i, result in enumerate(high_impact, 1):
                        reg = result['regulation']
                        f.write(f"{i}. {reg.get('nom_loi', '')}\n")
                        f.write(f"   Score: {result['total_score']:.3f}\n")
                        f.write(f"   ID: {reg.get('id_loi', 'N/A')}\n")
                        f.write(f"   Type: {reg.get('type', 'N/A')}\n")
                        f.write(f"   Pays concernés: {reg.get('pays_concernes', 'N/A')}\n")
                        f.write(f"   Date effet: {reg.get('date_effet', 'N/A')}\n")
                        f.write(f"   Date vigueur: {reg.get('date_vigueur', 'N/A')}\n\n")

                f.write("\n" + "="*70 + "\n")
                f.write("ANALYSE LLM:\n")
                f.write("="*70 + "\n")
                f.write(llm_analysis)

            print(f"\n💾 Rapport sauvegardé: {filename}")

        else:
            print(f"\n⚠️ Aucune loi à impact élevé ou moyen détectée")
            print(f"Les réglementations actuelles ont des scores d'impact faibles pour Hutchinson")

        # Résumé final
        print(f"\n🎉 TEST AVEC DONNÉES RÉELLES TERMINÉ !")
        print(f"\n📊 RÉSUMÉ:")
        print(f"   • Réglementations analysées: {len(regulations)}")
        print(f"   • Lois critiques détectées: {len(high_impact)}")
        print(f"   • Lois à surveiller: {len(medium_impact)}")
        print(f"   • Score moyen d'impact: {sum(r['total_score'] for r in matching_results) / len(matching_results):.3f}")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_real_matching_score(regulation, hutchinson_profile):
    """Calcule le score de matching avec les données réelles"""

    score_details = {
        'geo_score': 0.0,
        'sector_score': 0.0,
        'keyword_score': 0.0,
        'total_score': 0.0
    }

    # 1. Score géographique (30%)
    hutch_geo = hutchinson_profile.get('geographical_presence', [])
    reg_countries = regulation.get('pays_concernes', [])

    if hutch_geo and reg_countries:
        # Convertir en sets pour intersection
        hutch_geo_set = set([str(country).strip() for country in hutch_geo])
        reg_countries_set = set([str(country).strip() for country in reg_countries])

        geo_matches = len(hutch_geo_set & reg_countries_set)
        if geo_matches > 0:
            score_details['geo_score'] = min(1.0, geo_matches / len(reg_countries_set)) * 0.3

    # 2. Score sectoriel (40%)
    hutch_sectors = hutchinson_profile.get('company_info', {}).get('sectors', [])
    reg_sectors = regulation.get('secteurs', [])

    if hutch_sectors and reg_sectors:
        hutch_sectors_lower = [str(s).lower().strip() for s in hutch_sectors]
        reg_sectors_lower = [str(s).lower().strip() for s in reg_sectors]

        sector_matches = len(set(hutch_sectors_lower) & set(reg_sectors_lower))
        if sector_matches > 0:
            score_details['sector_score'] = min(1.0, sector_matches / len(reg_sectors_lower)) * 0.4

    # 3. Score mots-clés (30%)
    # Utiliser les mots-clés d'activité Hutchinson
    hutch_keywords = []
    if 'business_activities' in hutchinson_profile:
        for activity_list in hutchinson_profile['business_activities'].values():
            hutch_keywords.extend(activity_list)

    # Ajouter les matériaux
    if 'typical_materials' in hutchinson_profile:
        hutch_keywords.extend(hutchinson_profile['typical_materials'])

    reg_keywords = regulation.get('mots_cles', [])

    if hutch_keywords and reg_keywords:
        hutch_keywords_clean = [str(k).lower().replace('_', ' ') for k in hutch_keywords]
        reg_keywords_clean = [str(k).lower() for k in reg_keywords]

        keyword_matches = len(set(hutch_keywords_clean) & set(reg_keywords_clean))
        if keyword_matches > 0:
            score_details['keyword_score'] = min(1.0, keyword_matches / len(reg_keywords_clean)) * 0.3

    # 4. Score dans le texte (bonus)
    reg_text = str(regulation.get('texte', '')).lower()
    hutch_materials = hutchinson_profile.get('typical_materials', [])

    text_bonus = 0
    for material in hutch_materials:
        clean_material = str(material).replace('_', ' ').lower()
        if clean_material in reg_text:
            text_bonus += 0.02  # Petit bonus par matériau trouvé

    # Score total
    score_details['total_score'] = min(1.0,
        score_details['geo_score'] +
        score_details['sector_score'] +
        score_details['keyword_score'] +
        text_bonus
    )

    return score_details

if __name__ == "__main__":
    print("🎯 TEST AVEC VOS DONNÉES RÉELLES")
    print("Ce test va analyser les vraies réglementations dans votre base MongoDB")
    print("\n" + "="*60)

    success = test_with_real_data()

    if success:
        print(f"\n🚀 SYSTÈME TESTÉ AVEC SUCCÈS SUR VOS DONNÉES RÉELLES !")
        print(f"Votre système peut analyser et matcher les vraies réglementations")
        print(f"stockées dans votre collection MongoDB.")
    else:
        print(f"\n❌ Problème détecté avec les données réelles")
        print(f"Vérifiez que la base MongoDB contient des données")
