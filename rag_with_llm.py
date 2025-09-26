from rag_system import RegulatoryRiskRAG
import requests
import json
from datetime import datetime

class RegulatoryRiskRAGWithLLM(RegulatoryRiskRAG):
    """
    Extension du système RAG avec génération LLM pour des analyses plus poussées
    """

    def __init__(self, llm_provider="ollama"):
        super().__init__()
        self.llm_provider = llm_provider

    def generate_llm_analysis(self, report, company_profile):
        """
        ÉTAPE 3 - GENERATION : Utilise un LLM pour analyser et enrichir le rapport
        """
        # Construire le prompt pour le LLM
        prompt = self._build_analysis_prompt(report, company_profile)

        if self.llm_provider == "ollama":
            return self._call_ollama(prompt)
        elif self.llm_provider == "openai":
            return self._call_openai(prompt)
        else:
            return self._generate_rule_based_analysis(report, company_profile)

    def _build_analysis_prompt(self, report, company_profile):
        """Construit un prompt structuré pour l'analyse LLM"""

        # Extraire les informations clés du rapport
        high_risks = report["detailed_analysis"]["high_risk"]
        medium_risks = report["detailed_analysis"]["medium_risk"]

        prompt = f"""
Tu es un expert en conformité réglementaire et analyse de risques d'entreprise. 
Analyse le rapport de risques suivant et fournis une évaluation détaillée.

PROFIL ENTREPRISE:
Nom: {company_profile.get('nom', 'Non spécifié')}
Secteur: {company_profile.get('secteur', 'Non spécifié')}
Géographie: {', '.join(company_profile.get('presence_geographique', []))}
Matières premières: {', '.join(company_profile.get('matieres_premieres', []))}
Fournisseurs: {', '.join(company_profile.get('fournisseurs_regions', []))}

RISQUES DÉTECTÉS:
Risques élevés: {len(high_risks)}
Risques moyens: {len(medium_risks)}

RÉGLEMENTATIONS À HAUT RISQUE:
"""

        for i, risk in enumerate(high_risks[:3], 1):  # Top 3 risques
            reg = risk["regulation"]
            prompt += f"""
{i}. {reg.get('titre', 'Titre non disponible')}
   Score de similarité: {reg.get('score', 0):.4f}
   Impacts identifiés: {', '.join(risk['impact_details'])}
   Extrait réglementaire: {reg.get('texte', '')[:300]}...
"""

        prompt += f"""

ANALYSE DEMANDÉE:
1. Évalue la criticité globale pour cette entreprise (1-10)
2. Identifie les 3 actions prioritaires les plus urgentes
3. Estime l'impact financier potentiel (Faible/Moyen/Élevé)
4. Propose un calendrier de mise en conformité
5. Identifie les risques de non-conformité (sanctions, amendes, etc.)
6. Suggère des mesures préventives spécifiques au secteur

Format ta réponse de manière structurée avec des sections claires.
"""

        return prompt

    def _call_ollama(self, prompt):
        """Appelle un modèle Ollama local"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",  # ou un autre modèle disponible
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.json().get("response", "Erreur dans la génération")
            else:
                return f"Erreur Ollama: {response.status_code}"

        except requests.exceptions.RequestException as e:
            return f"Erreur de connexion Ollama: {e}"

    def _call_openai(self, prompt):
        """Appelle l'API OpenAI (nécessite une clé API)"""
        # Cette fonction nécessiterait une clé API OpenAI
        return "Fonction OpenAI non implémentée - clé API requise"

    def _generate_rule_based_analysis(self, report, company_profile):
        """Génération d'analyse basée sur des règles (fallback)"""
        analysis = []

        high_risk_count = report["risk_summary"]["high_risk_count"]
        medium_risk_count = report["risk_summary"]["medium_risk_count"]

        # Évaluation de criticité
        criticality = min(10, (high_risk_count * 3) + (medium_risk_count * 1.5))

        analysis.append(f"🎯 CRITICITÉ GLOBALE: {criticality:.1f}/10")

        if criticality >= 7:
            analysis.append("⚠️ NIVEAU D'ALERTE: CRITIQUE - Action immédiate requise")
        elif criticality >= 4:
            analysis.append("⚠️ NIVEAU D'ALERTE: MODÉRÉ - Surveillance renforcée")
        else:
            analysis.append("✅ NIVEAU D'ALERTE: FAIBLE - Monitoring de routine")

        # Actions prioritaires
        analysis.append("\n🚀 ACTIONS PRIORITAIRES:")
        if high_risk_count > 0:
            analysis.append("1. Audit de conformité immédiat pour les risques élevés")
            analysis.append("2. Consultation juridique spécialisée")
            analysis.append("3. Mise à jour des procédures internes")

        # Impact financier
        financial_impact = "Élevé" if high_risk_count > 2 else "Moyen" if high_risk_count > 0 else "Faible"
        analysis.append(f"\n💰 IMPACT FINANCIER ESTIMÉ: {financial_impact}")

        # Calendrier
        analysis.append("\n📅 CALENDRIER RECOMMANDÉ:")
        analysis.append("- Semaines 1-2: Audit et évaluation détaillée")
        analysis.append("- Mois 1-3: Mise en conformité prioritaire")
        analysis.append("- Mois 3-6: Implémentation complète")

        # Risques de non-conformité
        analysis.append("\n⚖️ RISQUES DE NON-CONFORMITÉ:")
        secteur = company_profile.get('secteur', '').lower()
        if 'industrie' in secteur or 'manufacturing' in secteur:
            analysis.append("- Amendes CBAM potentielles: 10-100€ par tonne CO2")
            analysis.append("- Restrictions d'importation possibles")

        analysis.append("- Sanctions administratives")
        analysis.append("- Impact sur la réputation")

        return "\n".join(analysis)

    def get_comprehensive_risk_assessment(self, company_profile, specific_query=None, use_llm=True):
        """
        Évaluation complète avec analyse LLM
        """
        # Obtenir le rapport de base
        base_report = self.get_regulatory_risk_assessment(company_profile, specific_query)

        if "error" in base_report:
            return base_report

        # Ajouter l'analyse LLM si demandée
        if use_llm:
            print("🤖 Génération de l'analyse LLM...")
            llm_analysis = self.generate_llm_analysis(base_report, company_profile)
            base_report["llm_analysis"] = llm_analysis

        return base_report

    def format_comprehensive_report(self, report):
        """Formate le rapport complet avec analyse LLM"""
        base_format = self.format_risk_report(report)

        if "llm_analysis" in report:
            llm_section = f"""
🤖 ANALYSE AVANCÉE PAR IA:
{report["llm_analysis"]}

{'='*80}
"""
            # Insérer l'analyse LLM avant la ligne de fin
            base_format = base_format.replace("=" * 80, llm_section)

        return base_format

def interactive_risk_consultant():
    """Interface interactive pour consultation de risques réglementaires"""

    print("🏢 CONSULTANT IA - RISQUES RÉGLEMENTAIRES")
    print("=" * 60)

    # Sélection du mode LLM
    print("1. Analyse standard (rapide)")
    print("2. Analyse avec LLM Ollama (nécessite Ollama)")
    print("3. Analyse avec règles avancées")

    mode = input("\nChoisissez le mode (1-3): ").strip()
    use_llm = mode == "2"

    rag = RegulatoryRiskRAGWithLLM("ollama" if use_llm else "rules")

    # Saisie du profil entreprise
    print("\n📋 PROFIL ENTREPRISE:")
    company_profile = {
        "nom": input("Nom de l'entreprise: ").strip(),
        "secteur": input("Secteur d'activité: ").strip(),
        "presence_geographique": input("Présence géographique (séparé par des virgules): ").split(","),
        "matieres_premieres": input("Matières premières utilisées (séparé par des virgules): ").split(","),
        "fournisseurs_regions": input("Régions des fournisseurs (séparé par des virgules): ").split(","),
    }

    # Nettoyer les listes
    for key in ["presence_geographique", "matieres_premieres", "fournisseurs_regions"]:
        company_profile[key] = [item.strip() for item in company_profile[key] if item.strip()]

    # Question spécifique (optionnelle)
    specific_query = input("\nQuestion spécifique (optionnel): ").strip()
    if not specific_query:
        specific_query = None

    print("\n" + "="*60)
    print("🔍 ANALYSE EN COURS...")

    try:
        report = rag.get_comprehensive_risk_assessment(
            company_profile,
            specific_query,
            use_llm=(mode == "2")
        )

        formatted_report = rag.format_comprehensive_report(report)
        print(formatted_report)

        # Sauvegarder le rapport
        filename = f"risk_report_{company_profile['nom'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_report)
        print(f"\n💾 Rapport sauvegardé: {filename}")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

if __name__ == "__main__":
    interactive_risk_consultant()
