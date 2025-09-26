from sentence_transformers import SentenceTransformer
from db import db
import json
from datetime import datetime
import re

# Modèle d'embedding
model = SentenceTransformer("all-MiniLM-L6-v2")

class HutchinsonRegulatoryAnalyzer:
    """
    Système d'analyse des risques réglementaires spécialisé pour Hutchinson
    Analyse l'impact des réglementations sur les secteurs, sites et activités
    """

    def __init__(self):
        self.model = model
        self.regulations = db["regulations"]  # Collection des données scrapées
        self.hutchinson = db["hutchinson"]    # Collection profil Hutchinson
        self.risk_analysis = db["risk_analysis"]  # Collection des analyses

        # Charger le profil Hutchinson
        self.hutchinson_profile = self.hutchinson.find_one({})
        if not self.hutchinson_profile:
            raise Exception("Profil Hutchinson non trouvé dans la base de données")

    def analyze_regulation_impact_on_hutchinson(self, regulation_id):
        """
        Analyse l'impact d'une réglementation spécifique sur Hutchinson

        Args:
            regulation_id (str): ID de la réglementation à analyser

        Returns:
            dict: Analyse complète de l'impact
        """
        # Récupérer la réglementation
        regulation = self.regulations.find_one({"id_loi": regulation_id})
        if not regulation:
            return {"error": f"Réglementation {regulation_id} non trouvée"}

        print(f"🔍 Analyse de la réglementation {regulation_id} pour Hutchinson...")

        # Analyse complète
        analysis = {
            "regulation_info": {
                "id_loi": regulation.get("id_loi"),
                "nom_loi": regulation.get("nom_loi"),
                "type": regulation.get("type"),
                "lien_loi": regulation.get("lien_loi"),
                "date_publication": regulation.get("date_publication"),
                "date_effet": regulation.get("date_effet"),
                "date_vigueur": regulation.get("date_vigueur"),
                "pays_concernes": regulation.get("pays_concernes", [])
            },
            "hutchinson_impact": {
                "secteurs_impactes": self._analyze_sector_impact(regulation),
                "sites_impactes": self._analyze_site_impact(regulation),
                "materiaux_impactes": self._analyze_material_impact(regulation),
                "activites_impactees": self._analyze_activity_impact(regulation),
                "sanctions_detectees": self._extract_sanctions(regulation),
                "score_risque": 0,  # Calculé plus tard
                "niveau_impact": "FAIBLE"  # Calculé plus tard
            },
            "analysis_date": datetime.now(),
            "status": "ANALYZED"
        }

        # Calculer le score de risque global
        analysis["hutchinson_impact"]["score_risque"] = self._calculate_risk_score(analysis)
        analysis["hutchinson_impact"]["niveau_impact"] = self._determine_impact_level(
            analysis["hutchinson_impact"]["score_risque"]
        )

        # Sauvegarder l'analyse
        self._save_analysis(analysis)

        return analysis

    def _analyze_sector_impact(self, regulation):
        """Analyse quel secteur Hutchinson est impacté"""
        secteurs_impactes = []
        reg_text = regulation.get("texte", "").lower()

        hutchinson_sectors = self.hutchinson_profile["company_info"]["sectors"]

        # Mapping des secteurs avec mots-clés
        sector_keywords = {
            "Automotive": ["automotive", "automobile", "vehicle", "car", "transport", "emission"],
            "Aerospace": ["aerospace", "aviation", "aircraft", "flight", "aeronautical"],
            "Industry": ["industrial", "manufacturing", "factory", "production"],
            "Railway": ["railway", "train", "rail", "transport"]
        }

        for sector in hutchinson_sectors:
            keywords = sector_keywords.get(sector, [sector.lower()])
            if any(keyword in reg_text for keyword in keywords):
                secteurs_impactes.append({
                    "secteur": sector,
                    "confidence": 0.8,  # Peut être amélioré avec ML
                    "mots_cles_detectes": [kw for kw in keywords if kw in reg_text]
                })

        return secteurs_impactes

    def _analyze_site_impact(self, regulation):
        """Analyse quels sites/pays Hutchinson sont impactés"""
        sites_impactes = []
        reg_text = regulation.get("texte", "").lower()
        pays_reg = regulation.get("pays_concernes", [])

        hutchinson_presence = self.hutchinson_profile["geographical_presence"]

        for pays in hutchinson_presence:
            # Impact direct si le pays est dans la réglementation
            if any(pays.lower() in p.lower() for p in pays_reg):
                sites_impactes.append({
                    "pays": pays,
                    "type_impact": "DIRECT",
                    "raison": f"Pays {pays} directement mentionné dans la réglementation"
                })
            # Impact indirect si mentionné dans le texte
            elif pays.lower() in reg_text:
                sites_impactes.append({
                    "pays": pays,
                    "type_impact": "INDIRECT",
                    "raison": f"Pays {pays} mentionné dans le contenu"
                })

        return sites_impactes

    def _analyze_material_impact(self, regulation):
        """Analyse quels matériaux Hutchinson sont impactés"""
        materiaux_impactes = []
        reg_text = regulation.get("texte", "").lower()

        hutchinson_materials = self.hutchinson_profile["typical_materials"]

        # Mapping matériaux avec synonymes
        material_synonyms = {
            "natural_rubber": ["rubber", "latex", "caoutchouc"],
            "synthetic_rubber": ["synthetic", "polymers", "elastomer"],
            "steel": ["steel", "metal", "iron", "acier"],
            "aluminum": ["aluminum", "aluminium", "alu"],
            "plastics": ["plastic", "polymer", "resin", "plastique"],
            "chemicals": ["chemical", "chimique", "substance"]
        }

        for material in hutchinson_materials:
            synonyms = material_synonyms.get(material, [material])
            detected_terms = [term for term in synonyms if term in reg_text]

            if detected_terms:
                materiaux_impactes.append({
                    "materiau": material,
                    "termes_detectes": detected_terms,
                    "impact_potentiel": "MOYEN"  # Peut être affiné
                })

        return materiaux_impactes

    def _analyze_activity_impact(self, regulation):
        """Analyse quelles activités Hutchinson sont impactées"""
        activites_impactees = []
        reg_text = regulation.get("texte", "").lower()

        hutchinson_activities = self.hutchinson_profile["business_activities"]

        # Analyse par secteur d'activité
        activity_keywords = {
            "sealing_systems": ["sealing", "seal", "gasket", "étanchéité"],
            "vibration_control": ["vibration", "damper", "shock", "amortisseur"],
            "fluid_transfer": ["fluid", "hose", "pipe", "transfer", "fluide"],
            "shock_absorbers": ["shock", "absorber", "damping", "amortisseur"],
            "anti_vibration": ["anti-vibration", "vibration", "isolation"]
        }

        for sector, activities in hutchinson_activities.items():
            for activity in activities:
                keywords = activity_keywords.get(activity, [activity.replace("_", " ")])
                detected = [kw for kw in keywords if kw in reg_text]

                if detected:
                    activites_impactees.append({
                        "secteur": sector,
                        "activite": activity,
                        "mots_cles_detectes": detected,
                        "niveau_impact": "POTENTIEL"
                    })

        return activites_impactees

    def _extract_sanctions(self, regulation):
        """Extrait les sanctions mentionnées dans le texte"""
        sanctions = []
        reg_text = regulation.get("texte", "")

        # Patterns pour détecter les sanctions
        sanction_patterns = [
            r"fine[s]?\s+of\s+(?:up\s+to\s+)?([€$£]\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:million|thousand))?)",
            r"penalty[ies]?\s+(?:up\s+to\s+)?([€$£]\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:million|thousand))?)",
            r"sanction[s]?\s+(?:up\s+to\s+)?([€$£]\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:million|thousand))?)",
            r"amende[s]?\s+(?:jusqu'à\s+)?(\d+(?:\s*(?:millions?\s+)?[€])?)",
            r"imprisonment\s+(?:up\s+to\s+)?(\d+\s+(?:years?|months?))",
            r"emprisonnement\s+(?:jusqu'à\s+)?(\d+\s+(?:ans?|mois))"
        ]

        for pattern in sanction_patterns:
            matches = re.finditer(pattern, reg_text, re.IGNORECASE)
            for match in matches:
                sanctions.append({
                    "type": "FINANCIERE" if any(symbol in match.group() for symbol in ["€", "$", "£"]) else "PENALE",
                    "montant_ou_duree": match.group(1) if match.groups() else "Non spécifié",
                    "contexte": reg_text[max(0, match.start()-50):match.end()+50]
                })

        # Sanctions génériques si aucune spécifique trouvée
        if not sanctions:
            generic_sanctions = ["sanction", "penalty", "fine", "amende", "punish"]
            if any(term in reg_text.lower() for term in generic_sanctions):
                sanctions.append({
                    "type": "GENERIQUE",
                    "montant_ou_duree": "Non spécifié",
                    "contexte": "Sanctions mentionnées sans détails précis"
                })

        return sanctions

    def _calculate_risk_score(self, analysis):
        """Calcule un score de risque global (0-100)"""
        score = 0
        impact = analysis["hutchinson_impact"]

        # Points par secteur impacté
        score += len(impact["secteurs_impactes"]) * 15

        # Points par site impacté
        direct_sites = len([s for s in impact["sites_impactes"] if s["type_impact"] == "DIRECT"])
        indirect_sites = len([s for s in impact["sites_impactes"] if s["type_impact"] == "INDIRECT"])
        score += direct_sites * 20 + indirect_sites * 10

        # Points par matériau impacté
        score += len(impact["materiaux_impactes"]) * 10

        # Points par activité impactée
        score += len(impact["activites_impactees"]) * 12

        # Points par sanction détectée
        financial_sanctions = len([s for s in impact["sanctions_detectees"] if s["type"] == "FINANCIERE"])
        score += financial_sanctions * 25
        score += (len(impact["sanctions_detectees"]) - financial_sanctions) * 15

        # Bonus si la réglementation est récente
        reg_date = analysis["regulation_info"].get("date_publication")
        if reg_date and (datetime.now() - reg_date).days < 365:
            score += 10

        return min(100, score)  # Cap à 100

    def _determine_impact_level(self, score):
        """Détermine le niveau d'impact basé sur le score"""
        if score >= 70:
            return "CRITIQUE"
        elif score >= 50:
            return "ELEVE"
        elif score >= 30:
            return "MOYEN"
        else:
            return "FAIBLE"

    def _save_analysis(self, analysis):
        """Sauvegarde l'analyse dans la collection risk_analysis"""
        # Vérifier si une analyse existe déjà
        existing = self.risk_analysis.find_one({
            "regulation_info.id_loi": analysis["regulation_info"]["id_loi"]
        })

        if existing:
            # Mettre à jour
            self.risk_analysis.update_one(
                {"_id": existing["_id"]},
                {"$set": analysis}
            )
            print(f"✅ Analyse mise à jour pour {analysis['regulation_info']['id_loi']}")
        else:
            # Créer nouvelle
            self.risk_analysis.insert_one(analysis)
            print(f"✅ Nouvelle analyse créée pour {analysis['regulation_info']['id_loi']}")

    def analyze_all_regulations(self):
        """Analyse toutes les réglementations pour Hutchinson"""
        print("🚀 Analyse de toutes les réglementations pour Hutchinson...")

        all_regulations = list(self.regulations.find({}))
        results = []

        for reg in all_regulations:
            try:
                analysis = self.analyze_regulation_impact_on_hutchinson(reg["id_loi"])
                results.append(analysis)
                print(f"✅ {reg['id_loi']} - Score: {analysis['hutchinson_impact']['score_risque']}")
            except Exception as e:
                print(f"❌ Erreur pour {reg.get('id_loi', 'Unknown')}: {e}")

        return results

    def get_high_risk_regulations(self, min_score=50):
        """Récupère les réglementations à haut risque"""
        high_risk = list(self.risk_analysis.find({
            "hutchinson_impact.score_risque": {"$gte": min_score}
        }).sort("hutchinson_impact.score_risque", -1))

        return high_risk

    def detect_regulation_changes(self):
        """Détecte les changements dans les réglementations (système d'alerte)"""
        print("🔍 Détection des changements réglementaires...")

        # Récupérer les réglementations modifiées récemment
        recent_changes = list(self.regulations.find({
            "updated_at": {"$exists": True},
            "updated_at": {"$gte": datetime.now().replace(hour=0, minute=0, second=0)}
        }))

        alerts = []
        for reg in recent_changes:
            # Ré-analyser la réglementation modifiée
            new_analysis = self.analyze_regulation_impact_on_hutchinson(reg["id_loi"])

            # Comparer avec l'ancienne analyse
            old_analysis = self.risk_analysis.find_one({
                "regulation_info.id_loi": reg["id_loi"],
                "analysis_date": {"$lt": datetime.now().replace(hour=0, minute=0, second=0)}
            })

            if old_analysis:
                old_score = old_analysis["hutchinson_impact"]["score_risque"]
                new_score = new_analysis["hutchinson_impact"]["score_risque"]

                if abs(new_score - old_score) >= 10:  # Changement significatif
                    alerts.append({
                        "regulation_id": reg["id_loi"],
                        "type": "SCORE_CHANGE",
                        "old_score": old_score,
                        "new_score": new_score,
                        "impact_change": new_score - old_score,
                        "date": datetime.now()
                    })

        return alerts

    def format_analysis_report(self, analysis):
        """Formate un rapport d'analyse pour affichage"""
        if "error" in analysis:
            return f"❌ {analysis['error']}"

        reg_info = analysis["regulation_info"]
        impact = analysis["hutchinson_impact"]

        output = []
        output.append("=" * 80)
        output.append("🏭 ANALYSE D'IMPACT RÉGLEMENTAIRE - HUTCHINSON")
        output.append("=" * 80)

        # Info réglementation
        output.append(f"📋 Réglementation: {reg_info['nom_loi']}")
        output.append(f"🆔 ID: {reg_info['id_loi']}")
        output.append(f"🔗 Lien: {reg_info['lien_loi']}")
        output.append(f"📅 Date publication: {reg_info['date_publication']}")
        output.append(f"⚖️ Type: {reg_info['type']}")
        output.append(f"🌍 Pays concernés: {', '.join(reg_info['pays_concernes'])}")
        output.append("")

        # Score et niveau
        score = impact["score_risque"]
        niveau = impact["niveau_impact"]
        color = {"CRITIQUE": "🔴", "ELEVE": "🟠", "MOYEN": "🟡", "FAIBLE": "🟢"}[niveau]

        output.append(f"📊 SCORE DE RISQUE: {score}/100")
        output.append(f"{color} NIVEAU D'IMPACT: {niveau}")
        output.append("")

        # Secteurs impactés
        if impact["secteurs_impactes"]:
            output.append("🏭 SECTEURS HUTCHINSON IMPACTÉS:")
            for secteur in impact["secteurs_impactes"]:
                output.append(f"  • {secteur['secteur']} (Confiance: {secteur['confidence']})")
                output.append(f"    Mots-clés: {', '.join(secteur['mots_cles_detectes'])}")
            output.append("")

        # Sites impactés
        if impact["sites_impactes"]:
            output.append("🌍 SITES HUTCHINSON IMPACTÉS:")
            for site in impact["sites_impactes"]:
                icon = "🎯" if site["type_impact"] == "DIRECT" else "〰️"
                output.append(f"  {icon} {site['pays']} ({site['type_impact']})")
                output.append(f"    Raison: {site['raison']}")
            output.append("")

        # Sanctions
        if impact["sanctions_detectees"]:
            output.append("⚖️ SANCTIONS IDENTIFIÉES:")
            for sanction in impact["sanctions_detectees"]:
                output.append(f"  • Type: {sanction['type']}")
                output.append(f"    Montant/Durée: {sanction['montant_ou_duree']}")
                output.append(f"    Contexte: {sanction['contexte'][:100]}...")
            output.append("")

        output.append("=" * 80)

        return "\n".join(output)

    def _calculate_business_relevance_score(self, regulation):
        """
        Calcule un score de pertinence métier intelligent (0-1)
        Plus le score est élevé, plus la réglementation est pertinente pour Hutchinson
        """
        reg_text = regulation.get("texte", "").lower()
        reg_title = regulation.get("nom_loi", "").lower()

        relevance_score = 0.0

        # 1. CORRESPONDANCES DIRECTES MÉTIER HUTCHINSON (poids fort)
        hutchinson_core_terms = {
            # Produits principaux
            "sealing": 0.9, "seal": 0.9, "gasket": 0.8, "étanchéité": 0.9,
            "vibration": 0.9, "damper": 0.8, "shock": 0.8, "amortisseur": 0.9,
            "rubber": 0.8, "elastomer": 0.8, "caoutchouc": 0.8,

            # Secteurs d'activité
            "automotive": 0.7, "automobile": 0.7, "vehicle": 0.6, "car": 0.5,
            "aerospace": 0.8, "aircraft": 0.8, "aviation": 0.7, "aeronautical": 0.7,
            "railway": 0.6, "train": 0.6, "rail": 0.6,

            # Matériaux utilisés
            "steel": 0.4, "aluminum": 0.4, "plastic": 0.4, "composite": 0.5,
            "fluid": 0.6, "hose": 0.7, "pipe": 0.4
        }

        # Calculer le score basé sur les termes détectés
        for term, weight in hutchinson_core_terms.items():
            if term in reg_text or term in reg_title:
                relevance_score += weight

        # 2. INDICATEURS DE NON-PERTINENCE (réduction du score)
        irrelevant_terms = {
            # Secteurs sans rapport
            "pharmaceutical": -0.8, "drug": -0.7, "medicine": -0.7, "clinical": -0.6,
            "medicinal": -0.7, "patient": -0.6, "healthcare": -0.5, "medical": -0.6,

            # Autres secteurs non pertinents
            "banking": -0.7, "financial": -0.5, "insurance": -0.5,
            "retail": -0.6, "shopping": -0.5, "consumer": -0.3,
            "telecommunications": -0.6, "telecom": -0.6, "internet": -0.4,
            "agriculture": -0.4, "farming": -0.4, "food": -0.3,

            # Termes médicaux spécifiques
            "tablet": -0.5, "capsule": -0.5, "injection": -0.6, "sterile": -0.6,
            "clinical trial": -0.8, "human subjects": -0.7
        }

        for term, penalty in irrelevant_terms.items():
            if term in reg_text or term in reg_title:
                relevance_score += penalty  # Réduction du score

        # 3. BONUS POUR CONTEXTE MANUFACTURING
        manufacturing_terms = ["manufacturing", "production", "factory", "facility", "plant"]
        if any(term in reg_text for term in manufacturing_terms):
            relevance_score += 0.2

        # 4. NORMALISATION ET LIMITES
        # Assurer que le score reste dans [0, 1]
        relevance_score = max(0.0, min(1.0, relevance_score))

        return relevance_score

    def _assess_risk_level(self, regulation, company_profile):
        """Évalue le niveau de risque d'une réglementation pour l'entreprise"""
        score = regulation.get('score', 0)

        # NOUVELLE APPROCHE : Calculer d'abord la pertinence métier
        business_relevance = self._calculate_business_relevance_score(regulation)

        # Si la pertinence métier est très faible, forcer un niveau bas
        if business_relevance < 0.3:
            return "low"

        reg_text = regulation.get("texte", "").lower()

        # Facteurs de risque basés sur le profil entreprise
        risk_factors = 0

        # Géographie (pondéré par la pertinence métier)
        company_regions = company_profile.get('presence_geographique', [])
        if any(region.lower() in reg_text for region in company_regions):
            risk_factors += 0.3 * business_relevance

        # Activités métier spécifiques (pondéré par la pertinence)
        business_activities = company_profile.get("business_activities", {})
        for sector, activities in business_activities.items():
            for activity in activities:
                activity_terms = activity.replace("_", " ").split()
                if any(term in reg_text for term in activity_terms):
                    risk_factors += 0.2 * business_relevance
                    break

        # Matériaux utilisés (pondéré par la pertinence)
        materials = company_profile.get("typical_materials", [])
        for material in materials:
            material_terms = material.replace("_", " ").split()
            if any(term in reg_text for term in material_terms):
                risk_factors += 0.15 * business_relevance

        # Produits spécifiques (pondéré par la pertinence)
        products = company_profile.get("specific_products", [])
        for product in products:
            product_terms = product.replace("_", " ").split()
            if any(term in reg_text for term in product_terms):
                risk_factors += 0.25 * business_relevance

        # Score de similarité (pondéré par la pertinence)
        similarity_factor = min(score, 0.3) * business_relevance

        # Score final pondéré par la pertinence métier
        total_risk = (similarity_factor + risk_factors) * business_relevance

        if total_risk > 0.7:
            return "high"
        elif total_risk > 0.4:
            return "medium"
        else:
            return "low"

def demo_hutchinson_analysis():
    """Démonstration du système d'analyse Hutchinson"""

    print("🏭 SYSTÈME D'ANALYSE RÉGLEMENTAIRE HUTCHINSON")
    print("=" * 60)

    try:
        analyzer = HutchinsonRegulatoryAnalyzer()

        # Analyser toutes les réglementations
        print("🔍 Analyse de toutes les réglementations...")
        results = analyzer.analyze_all_regulations()

        print(f"\n📊 RÉSUMÉ DE L'ANALYSE ({len(results)} réglementations):")
        print("=" * 50)

        for result in results:
            if "error" not in result:
                reg_id = result["regulation_info"]["id_loi"]
                score = result["hutchinson_impact"]["score_risque"]
                niveau = result["hutchinson_impact"]["niveau_impact"]

                color = {"CRITIQUE": "🔴", "ELEVE": "🟠", "MOYEN": "🟡", "FAIBLE": "🟢"}[niveau]
                print(f"{color} {reg_id}: {score}/100 ({niveau})")

        # Afficher le rapport détaillé de la réglementation la plus risquée
        if results:
            highest_risk = max(results, key=lambda x: x.get("hutchinson_impact", {}).get("score_risque", 0))
            print(f"\n📄 RAPPORT DÉTAILLÉ - PLUS HAUT RISQUE:")
            print(analyzer.format_analysis_report(highest_risk))

        # Détection de changements (simulation)
        print("\n🚨 SYSTÈME D'ALERTE:")
        alerts = analyzer.detect_regulation_changes()
        if alerts:
            for alert in alerts:
                print(f"⚠️ {alert['regulation_id']}: Score changé de {alert['old_score']} à {alert['new_score']}")
        else:
            print("✅ Aucun changement significatif détecté")

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    demo_hutchinson_analysis()
