from sentence_transformers import SentenceTransformer
from db import db
import json
from datetime import datetime

# Modèle d'embedding
model = SentenceTransformer("all-MiniLM-L6-v2")

class RegulatoryRiskRAG:
    """
    Système RAG spécialisé pour l'anticipation des risques réglementaires
    Analyse CBAM, CSRD, EUDR, sanctions, droits de douanes, etc.
    """

    def __init__(self):
        self.model = model
        self.regulations = db["regulations"]

        # Types de risques réglementaires à surveiller
        self.risk_categories = {
            "cbam": ["CBAM", "Carbon Border Adjustment", "émissions carbone", "frontière carbone"],
            "csrd": ["CSRD", "Corporate Sustainability Reporting", "reporting durabilité"],
            "eudr": ["EUDR", "déforestation", "chaîne d'approvisionnement", "matières premières"],
            "sanctions": ["sanctions", "embargo", "restrictions commerciales", "pays sanctionnés"],
            "douanes": ["droits de douane", "tarifs douaniers", "import", "export"],
            "gdpr": ["RGPD", "GDPR", "protection données", "vie privée"],
            "supply_chain": ["chaîne d'approvisionnement", "fournisseurs", "due diligence"]
        }

    def retrieve_relevant_regulations(self, query_text, company_context=None, limit=5):
        """
        ÉTAPE 1 - RETRIEVAL : Récupère les réglementations pertinentes
        """
        # Enrichir la requête avec le contexte entreprise si fourni
        enriched_query = query_text
        if company_context:
            enriched_query += f" {company_context.get('secteur', '')} {company_context.get('geographie', '')}"

        query_embedding = self.model.encode(enriched_query).tolist()

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index_1",  # Nom mis à jour de l'index dans Atlas
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "id_loi": 1,
                    "titre": 1,
                    "texte": 1,
                    "date_promulgation": 1,
                    "jurisdiction": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        try:
            results = list(self.regulations.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"❌ Erreur lors de la récupération : {e}")
            return []

    def analyze_regulatory_impact(self, regulations, company_profile):
        """
        ÉTAPE 2 - ANALYSE D'IMPACT : Analyse l'impact des réglementations sur l'entreprise
        """
        impact_analysis = {
            "high_risk": [],
            "medium_risk": [],
            "low_risk": [],
            "recommendations": []
        }

        for reg in regulations:
            risk_level = self._assess_risk_level(reg, company_profile)
            impact_analysis[f"{risk_level}_risk"].append({
                "regulation": reg,
                "impact_details": self._get_specific_impact(reg, company_profile)
            })

        # Générer des recommandations
        impact_analysis["recommendations"] = self._generate_recommendations(
            impact_analysis, company_profile
        )

        return impact_analysis

    def _assess_risk_level(self, regulation, company_profile):
        """Évalue le niveau de risque d'une réglementation pour l'entreprise"""
        score = regulation.get('score', 0)

        # Facteurs de risque basés sur le profil entreprise
        risk_factors = 0

        # Géographie
        company_regions = company_profile.get('presence_geographique', [])
        reg_text = regulation.get('texte', '').lower()

        if any(region.lower() in reg_text for region in company_regions):
            risk_factors += 0.3

        # Secteur d'activité
        secteur = company_profile.get('secteur', '').lower()
        if secteur in reg_text:
            risk_factors += 0.4

        # Score de similarité
        similarity_factor = min(score, 0.3)

        total_risk = similarity_factor + risk_factors

        if total_risk > 0.7:
            return "high"
        elif total_risk > 0.4:
            return "medium"
        else:
            return "low"

    def _get_specific_impact(self, regulation, company_profile):
        """Détermine l'impact spécifique d'une réglementation"""
        impacts = []

        reg_text = regulation.get('texte', '').lower()

        # Impacts sur les matières premières
        if company_profile.get('matieres_premieres'):
            for matiere in company_profile['matieres_premieres']:
                if matiere.lower() in reg_text:
                    impacts.append(f"Impact sur matière première: {matiere}")

        # Impacts sur les fournisseurs
        if company_profile.get('fournisseurs_regions'):
            for region in company_profile['fournisseurs_regions']:
                if region.lower() in reg_text:
                    impacts.append(f"Impact sur fournisseurs région: {region}")

        # Impacts clients
        if company_profile.get('clients_regions'):
            for region in company_profile['clients_regions']:
                if region.lower() in reg_text:
                    impacts.append(f"Impact sur clients région: {region}")

        return impacts if impacts else ["Impact général sur les opérations"]

    def _generate_recommendations(self, impact_analysis, company_profile):
        """Génère des recommandations d'actions"""
        recommendations = []

        high_risks = len(impact_analysis["high_risk"])
        medium_risks = len(impact_analysis["medium_risk"])

        if high_risks > 0:
            recommendations.append({
                "priority": "URGENT",
                "action": f"Audit immédiat de conformité pour {high_risks} réglementation(s) à haut risque",
                "timeline": "1-2 semaines"
            })

        if medium_risks > 0:
            recommendations.append({
                "priority": "IMPORTANT",
                "action": f"Évaluation détaillée pour {medium_risks} réglementation(s) à risque moyen",
                "timeline": "1-2 mois"
            })

        # Recommandations spécifiques par secteur
        secteur = company_profile.get('secteur', '').lower()
        if 'manufacturing' in secteur or 'industrie' in secteur:
            recommendations.append({
                "priority": "PREVENTIF",
                "action": "Mise en place d'un système de monitoring carbone pour CBAM",
                "timeline": "3-6 mois"
            })

        return recommendations

    def get_regulatory_risk_assessment(self, company_profile, specific_query=None):
        """
        Fonction principale : Évaluation complète des risques réglementaires
        """
        print("🔍 Analyse des risques réglementaires en cours...")

        # Construire la requête basée sur le profil entreprise
        if specific_query:
            query = specific_query
        else:
            query_parts = []
            if company_profile.get('secteur'):
                query_parts.append(company_profile['secteur'])
            if company_profile.get('matieres_premieres'):
                query_parts.extend(company_profile['matieres_premieres'])
            if company_profile.get('presence_geographique'):
                query_parts.extend(company_profile['presence_geographique'])

            query = " ".join(query_parts)

        # Récupération des réglementations pertinentes
        relevant_regulations = self.retrieve_relevant_regulations(
            query, company_profile, limit=8
        )

        if not relevant_regulations:
            return {"error": "Aucune réglementation pertinente trouvée"}

        # Analyse d'impact
        impact_analysis = self.analyze_regulatory_impact(
            relevant_regulations, company_profile
        )

        # Formatage du rapport final
        report = {
            "company_profile": company_profile,
            "analysis_date": datetime.now().isoformat(),
            "total_regulations_analyzed": len(relevant_regulations),
            "risk_summary": {
                "high_risk_count": len(impact_analysis["high_risk"]),
                "medium_risk_count": len(impact_analysis["medium_risk"]),
                "low_risk_count": len(impact_analysis["low_risk"])
            },
            "detailed_analysis": impact_analysis,
            "query_used": query
        }

        return report

    def format_risk_report(self, report):
        """Formate le rapport de risques pour affichage"""
        if "error" in report:
            return f"❌ {report['error']}"

        output = []
        output.append("=" * 80)
        output.append("🚨 RAPPORT D'ANTICIPATION DES RISQUES RÉGLEMENTAIRES")
        output.append("=" * 80)

        # Profil entreprise
        profile = report["company_profile"]
        output.append(f"🏢 Entreprise: {profile.get('nom', 'Non spécifié')}")
        output.append(f"🏭 Secteur: {profile.get('secteur', 'Non spécifié')}")
        output.append(f"🌍 Présence géographique: {', '.join(profile.get('presence_geographique', []))}")
        output.append(f"📅 Date d'analyse: {report['analysis_date']}")
        output.append("")

        # Résumé des risques
        summary = report["risk_summary"]
        output.append("📊 RÉSUMÉ DES RISQUES:")
        output.append(f"🔴 Risques élevés: {summary['high_risk_count']}")
        output.append(f"🟡 Risques moyens: {summary['medium_risk_count']}")
        output.append(f"🟢 Risques faibles: {summary['low_risk_count']}")
        output.append("")

        # Détails par niveau de risque
        analysis = report["detailed_analysis"]

        for risk_level, color in [("high", "🔴"), ("medium", "🟡"), ("low", "🟢")]:
            risks = analysis[f"{risk_level}_risk"]
            if risks:
                output.append(f"{color} RISQUES {risk_level.upper()}:")
                for i, risk in enumerate(risks, 1):
                    reg = risk["regulation"]
                    output.append(f"  {i}. {reg.get('titre', 'Titre non disponible')}")
                    output.append(f"     ID: {reg.get('id_loi', 'N/A')}")
                    output.append(f"     Score: {reg.get('score', 0):.4f}")
                    output.append(f"     Impacts: {', '.join(risk['impact_details'])}")
                output.append("")

        # Recommandations
        recommendations = analysis["recommendations"]
        if recommendations:
            output.append("💡 RECOMMANDATIONS D'ACTIONS:")
            for i, rec in enumerate(recommendations, 1):
                output.append(f"  {i}. [{rec['priority']}] {rec['action']}")
                output.append(f"     ⏱️ Délai: {rec['timeline']}")
            output.append("")

        output.append("=" * 80)

        return "\n".join(output)

def demo_risk_assessment():
    """Démonstration du système avec des profils d'entreprise types"""
    rag = RegulatoryRiskRAG()

    # Exemples de profils d'entreprise
    company_profiles = [
        {
            "nom": "EcoManufacturing SA",
            "secteur": "manufacturing industrie",
            "presence_geographique": ["France", "Allemagne", "Chine"],
            "matieres_premieres": ["acier", "aluminium", "plastique"],
            "fournisseurs_regions": ["Chine", "Inde", "Brésil"],
            "clients_regions": ["Europe", "Amérique du Nord"]
        },
        {
            "nom": "GreenTech Solutions",
            "secteur": "technologie durable énergie",
            "presence_geographique": ["France", "États-Unis"],
            "matieres_premieres": ["lithium", "cobalt", "terres rares"],
            "fournisseurs_regions": ["République Démocratique du Congo", "Chili"],
            "clients_regions": ["Europe", "Amérique du Nord", "Asie"]
        }
    ]

    for profile in company_profiles:
        print(f"\n🔍 Analyse pour {profile['nom']}...")
        report = rag.get_regulatory_risk_assessment(profile)
        formatted_report = rag.format_risk_report(report)
        print(formatted_report)
        print("\n" + "="*100 + "\n")

if __name__ == "__main__":
    print("🚀 Démarrage du système RAG d'anticipation des risques réglementaires")
    demo_risk_assessment()
