#!/usr/bin/env python3
"""
Test du système de matching Hutchinson <-> Réglementations
Vérifie si le système peut identifier les lois pertinentes et calculer l'impact
"""

from pymongo import MongoClient
from datetime import datetime

def test_matching_system():
    """Test complet du matching réglementations <-> Hutchinson"""

    print("🎯 TEST DU SYSTÈME DE MATCHING HUTCHINSON")
    print("=" * 60)

    try:
        # Connexion MongoDB
        CONNECTION_STRING = "mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc"
        client = MongoClient(CONNECTION_STRING)
        db = client["hackathon_regulations"]

        # Récupérer le profil Hutchinson
        print("🏢 Récupération du profil Hutchinson...")
        hutchinson = db.hutchinson.find_one()

        if not hutchinson:
            print("❌ Profil Hutchinson non trouvé en base")
            return False

        print("✅ Profil Hutchinson récupéré")
        print(f"   • Secteurs: {hutchinson['company_info']['sectors']}")
        print(f"   • Géographie: {hutchinson['geographical_presence'][:5]}...")

        # Récupérer toutes les réglementations
        print("\n📚 Récupération des réglementations...")
        regulations = list(db.regulations.find())

        if not regulations:
            print("❌ Aucune réglementation trouvée en base")
            return False

        print(f"✅ {len(regulations)} réglementations récupérées")

        # ÉTAPE DE MATCHING
        print(f"\n🔍 ANALYSE DE MATCHING:")
        print("-" * 40)

        matched_results = []

        for reg in regulations:
            print(f"\n📋 {reg['nom_loi']}")

            # Calcul du score de matching
            score_details = calculate_matching_score(reg, hutchinson)
            total_score = score_details['total_score']

            # Classification d'impact
            if total_score >= 0.7:
                impact_level = "🔴 TRÈS ÉLEVÉ"
                priority = "URGENT"
            elif total_score >= 0.5:
                impact_level = "🟡 MOYEN"
                priority = "IMPORTANT"
            elif total_score >= 0.3:
                impact_level = "🟠 FAIBLE"
                priority = "SURVEILLLER"
            else:
                impact_level = "🟢 NÉGLIGEABLE"
                priority = "IGNORER"

            print(f"   🎯 Score total: {total_score:.3f}")
            print(f"   📊 Impact: {impact_level}")
            print(f"   ⏰ Priorité: {priority}")
            print(f"   📅 Date effet: {reg['date_effet'].strftime('%d/%m/%Y') if reg.get('date_effet') else 'N/A'}")
            print(f"   📅 Date vigueur: {reg['date_vigueur'].strftime('%d/%m/%Y') if reg.get('date_vigueur') else 'N/A'}")
            print(f"   💰 Sanctions: {reg.get('sanctions', 'Non spécifiées')}")

            # Détail du scoring
            print(f"   📈 Détail scores:")
            print(f"      • Géographie: {score_details['geo_score']:.2f}")
            print(f"      • Secteur: {score_details['sector_score']:.2f}")
            print(f"      • Mots-clés: {score_details['keyword_score']:.2f}")
            print(f"      • Matériaux: {score_details['material_score']:.2f}")

            matched_results.append({
                'regulation': reg,
                'total_score': total_score,
                'impact_level': impact_level,
                'priority': priority,
                'score_details': score_details
            })

        # RÉSULTATS TRIÉS PAR PERTINENCE
        print(f"\n🏆 RÉSULTATS TRIÉS PAR PERTINENCE:")
        print("=" * 60)

        # Trier par score décroissant
        matched_results.sort(key=lambda x: x['total_score'], reverse=True)

        high_impact = [r for r in matched_results if r['total_score'] >= 0.7]
        medium_impact = [r for r in matched_results if 0.5 <= r['total_score'] < 0.7]
        low_impact = [r for r in matched_results if 0.3 <= r['total_score'] < 0.5]
        negligible = [r for r in matched_results if r['total_score'] < 0.3]

        print(f"🔴 IMPACT TRÈS ÉLEVÉ ({len(high_impact)} lois):")
        for result in high_impact:
            reg = result['regulation']
            print(f"   • {reg['nom_loi']} (Score: {result['total_score']:.3f})")
            print(f"     ⚠️ Action requise avant {reg['date_effet'].strftime('%d/%m/%Y')}")

        print(f"\n🟡 IMPACT MOYEN ({len(medium_impact)} lois):")
        for result in medium_impact:
            reg = result['regulation']
            print(f"   • {reg['nom_loi']} (Score: {result['total_score']:.3f})")

        print(f"\n🟠 IMPACT FAIBLE ({len(low_impact)} lois):")
        for result in low_impact:
            reg = result['regulation']
            print(f"   • {reg['nom_loi']} (Score: {result['total_score']:.3f})")

        print(f"\n🟢 IMPACT NÉGLIGEABLE ({len(negligible)} lois):")
        for result in negligible:
            reg = result['regulation']
            print(f"   • {reg['nom_loi']} (Score: {result['total_score']:.3f})")

        print(f"\n📊 SYNTHÈSE POUR HUTCHINSON:")
        print(f"   • Lois à impact ÉLEVÉ: {len(high_impact)}")
        print(f"   • Lois à surveiller: {len(medium_impact)}")
        print(f"   • Lois peu pertinentes: {len(low_impact + negligible)}")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_matching_score(regulation, hutchinson_profile):
    """Calcule le score de matching entre une réglementation et Hutchinson"""

    score_details = {
        'geo_score': 0.0,
        'sector_score': 0.0,
        'keyword_score': 0.0,
        'material_score': 0.0,
        'total_score': 0.0
    }

    # 1. Score géographique (25% du total)
    hutch_geo = hutchinson_profile['geographical_presence']
    reg_countries = regulation.get('pays_concernes', [])

    geo_matches = len(set(hutch_geo) & set(reg_countries))
    if geo_matches > 0:
        score_details['geo_score'] = min(1.0, geo_matches / len(reg_countries)) * 0.25

    # 2. Score sectoriel (35% du total)
    hutch_sectors = [s.lower() for s in hutchinson_profile['company_info']['sectors']]
    reg_sectors = [s.lower() for s in regulation.get('secteurs', [])]

    sector_matches = len(set(hutch_sectors) & set(reg_sectors))
    if sector_matches > 0:
        score_details['sector_score'] = min(1.0, sector_matches / len(reg_sectors)) * 0.35

    # 3. Score mots-clés (25% du total)
    hutch_keywords = hutchinson_profile.get('keywords_matching', [])
    reg_keywords = regulation.get('mots_cles', [])

    keyword_matches = len(set(hutch_keywords) & set(reg_keywords))
    if keyword_matches > 0:
        score_details['keyword_score'] = min(1.0, keyword_matches / len(reg_keywords)) * 0.25

    # 4. Score matériaux (15% du total)
    hutch_materials = hutchinson_profile.get('materials', [])
    reg_text = regulation.get('texte', '').lower()

    material_mentions = sum(1 for material in hutch_materials if material.replace('_', ' ') in reg_text)
    if material_mentions > 0:
        score_details['material_score'] = min(1.0, material_mentions / len(hutch_materials)) * 0.15

    # Score total
    score_details['total_score'] = (
        score_details['geo_score'] +
        score_details['sector_score'] +
        score_details['keyword_score'] +
        score_details['material_score']
    )

    return score_details

if __name__ == "__main__":
    success = test_matching_system()

    if success:
        print("\n✅ TEST DE MATCHING RÉUSSI !")
        print("\n🎯 VOTRE SYSTÈME PEUT:")
        print("   • ✅ Lire les lois de la collection 'regulations'")
        print("   • ✅ Matcher avec le profil Hutchinson")
        print("   • ✅ Calculer des scores d'impact")
        print("   • ✅ Trier par pertinence")
        print("   • ✅ Afficher dates d'effet et sanctions")
        print("   • ✅ Classer par niveau de priorité")
    else:
        print("\n❌ PROBLÈME DÉTECTÉ - Vérifiez la base MongoDB")
