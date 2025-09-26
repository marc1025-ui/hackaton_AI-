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
        ÉTAPE 3 - GENERATION : Utilise TOUJOURS un LLM pour analyser et enrichir le rapport
        """
        # Construire le prompt pour le LLM
        prompt = self._build_analysis_prompt(report, company_profile)

        if self.llm_provider == "ollama":
            return self._call_ollama(prompt)
        # elif self.llm_provider == "openai":
        #     return self._call_openai(prompt)
        else:
            # Commenter le système de règles - TOUT passe par LLM maintenant
            # return self._generate_rule_based_analysis(report, company_profile)
            return self._call_ollama(prompt)  # Forcer l'utilisation du LLM

    def _build_analysis_prompt(self, report, company_profile):
        """Construit un prompt optimisé pour retourner UNIQUEMENT les données UI basé sur le profil réel de Hutchinson"""

        # Extraire TOUTES les informations clés du rapport (sans limite)
        high_risks = report["detailed_analysis"]["high_risk"]  # Toutes les lois high risk
        medium_risks = report["detailed_analysis"]["medium_risk"]  # Toutes les lois medium risk
        low_risks = report["detailed_analysis"]["low_risk"]  # Toutes les lois low risk (limite supprimée)

        # Construire les secteurs d'activité réels depuis le profil MongoDB
        secteurs_reels = company_profile.get('secteur', 'automobile aerospace manufacturing industrie')
        presence_geo = company_profile.get('presence_geographique', [])
        matieres_premieres = company_profile.get('matieres_premieres', [])
        secteurs_clients = company_profile.get('secteurs_clients', [])

        prompt = f"""Tu es un expert en conformité réglementaire. Analyse ces réglementations pour {company_profile.get('nom', 'Hutchinson')}.

PROFIL RÉEL HUTCHINSON (depuis base de données):
- Nom: {company_profile.get('nom', 'Hutchinson')}
- Secteurs d'activité: {secteurs_reels}
- Présence géographique: {', '.join(presence_geo[:10]) if presence_geo else 'International'}
- Matières premières utilisées: {', '.join(matieres_premieres[:8]) if matieres_premieres else 'Caoutchouc, polymères, métaux'}
- Secteurs clients: {', '.join(secteurs_clients) if secteurs_clients else 'Automobile, aéronautique, industrie'}

ACTIVITÉS SPÉCIFIQUES HUTCHINSON:
- Systèmes d'étanchéité (sealing systems)
- Contrôle des vibrations (vibration control) 
- Transfert de fluides (fluid transfer)
- Amortisseurs et suspensions
- Composants en caoutchouc et polymères
- Pièces métalliques et assemblages

TOUTES LES RÉGLEMENTATIONS À ANALYSER:"""

        all_risks = high_risks + medium_risks + low_risks
        for i, risk in enumerate(all_risks, 1):
            reg = risk["regulation"]
            deadline = reg.get('date_effet') or reg.get('date_vigueur')
            deadline_str = deadline.strftime('%d/%m/%Y') if deadline else "Non définie"

            # Récupérer la vraie URL depuis les données
            real_url = reg.get('lien_loi') or reg.get('url') or reg.get('law_url') or "#"

            prompt += f"""

{i}. {reg.get('nom_loi', 'Loi non nommée')}
   URL: {real_url}
   Date limite: {deadline_str}
   Sanctions: {reg.get('sanctions', 'Non spécifiées')}
   Texte: {str(reg.get('texte', ''))[:200]}...
"""

        prompt += f"""

FILTRAGE STRICT - Tu dois identifier UNIQUEMENT les réglementations qui impactent DIRECTEMENT les activités réelles de Hutchinson.

SECTEURS D'ACTIVITÉ HUTCHINSON À MATCHER:
✅ INCLURE SEULEMENT si la loi concerne:
- Industrie automobile (composants, équipementiers)
- Industrie aéronautique et aérospatiale
- Manufacturing et production industrielle
- Matériaux: caoutchouc, polymères, élastomères, métaux
- Systèmes d'étanchéité et joints
- Contrôle des vibrations et amortisseurs
- Normes de sécurité industrielle
- Réglementations environnementales pour l'industrie
- Commerce international et export
- Pays où Hutchinson opère: {', '.join(presence_geo[:8]) if presence_geo else 'France, États-Unis, Chine, Allemagne'}

❌ EXCLURE TOTALEMENT si la loi concerne:
- Industrie pharmaceutique (Hutchinson ne fait PAS de pharma)
- Secteur médical et dispositifs médicaux
- Agriculture et agroalimentaire
- Services financiers et banques
- Télécommunications et IT
- Énergie nucléaire
- Secteurs sans lien avec manufacturing industriel

Retourne EXACTEMENT ce format JSON (SEULEMENT les lois pertinentes pour les activités réelles de Hutchinson):

{{
  "indicators": [
    {{
      "law_name": "Nom exact de la loi pertinente pour Hutchinson",
      "law_url": "URL complète exacte de la loi (utilise la vraie URL fournie ci-dessus)",
      "deadline": "DD/MM/YYYY",
      "impact_financial": 9,
      "impact_reputation": 8,
      "impact_operational": 6,
      "notes": "Pourquoi cette loi impacte spécifiquement Hutchinson (80 chars max)",
      "sector_match": "Secteur Hutchinson concerné (ex: automobile, aéronautique, manufacturing)"
    }}
  ]
}}

RÈGLES STRICTES D'ANALYSE:
1. VÉRIFICATION OBLIGATOIRE: La loi doit avoir un lien DIRECT avec les secteurs d'activité réels de Hutchinson
2. Si AUCUNE loi ne correspond aux activités de Hutchinson, retourne: {{"indicators": []}}
3. Impact financier (1-10): Basé sur les sanctions et amendes pour les activités de Hutchinson
4. Impact réputation (1-10): Risque d'image pour un équipementier automobile/aéronautique
5. Impact opérationnel (1-10): Complexité de mise en conformité dans les usines Hutchinson
6. sector_match: Précise exactement quel secteur Hutchinson est concerné
7. law_url: OBLIGATOIRE - Utilise exactement l'URL fournie dans la section ci-dessus

VALIDATION FINALE:
Avant de retourner une loi, pose-toi la question:
"Est-ce que cette réglementation impacte réellement une entreprise qui fabrique des joints d'étanchéité, des amortisseurs et des composants en caoutchouc pour l'automobile et l'aéronautique?"

Si la réponse est NON, n'inclus pas cette loi.

IMPORTANT:
1. Retourne SEULEMENT le JSON valide avec les vraies lois pertinentes
2. Si aucune loi ne correspond, retourne un tableau vide
3. Utilise les VRAIES URLs fournies ci-dessus, pas "#"
4. Aucun texte en plus du JSON."""

        return prompt

    def _call_ollama(self, prompt):
        """Appelle un modèle Ollama local"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",  # Changé pour utiliser llama2
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

    # MÉTHODES COMMENTÉES - NE SONT PLUS UTILISÉES (TOUT PASSE PAR LLM)
    # def _generate_rule_based_analysis(self, report, company_profile):
    #     """Génération d'analyse basée sur des règles (fallback) - COMMENTÉ"""
    #     pass

    # def _calculate_financial_impact(self, regulation, risk):
    #     """Calcule l'impact financier sur 10 - COMMENTÉ"""
    #     pass

    # def _calculate_reputation_impact(self, regulation, risk):
    #     """Calcule l'impact réputation sur 10 - COMMENTÉ"""
    #     pass

    # def _calculate_operational_impact(self, regulation, risk):
    #     """Calcule l'impact opérationnel sur 10 - COMMENTÉ"""
    #     pass

    # def _generate_explanatory_notes(self, regulation, impact_fin, impact_rep, impact_op):
    #     """Génère les notes explicatives intelligentes - COMMENTÉ"""
    #     pass

    def extract_ui_data_from_llm_response(self, llm_response):
        """
        Extrait les données JSON du LLM pour l'interface utilisateur
        Le LLM fait directement le filtrage des secteurs pertinents
        """
        try:
            # DEBUG: Afficher la réponse brute du LLM
            print(f"\n🔧 DEBUG - Réponse brute du LLM:")
            print(f"Type: {type(llm_response)}")
            print(f"Contenu: {str(llm_response)[:500]}...")
            print("-" * 50)

            # Essayer de parser directement comme JSON
            if isinstance(llm_response, str):
                # Nettoyer la réponse si elle contient du texte en plus
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    print(f"🔧 DEBUG - JSON extrait: {json_str[:200]}...")

                    data = json.loads(json_str)

                    # Vérifier que les données ont la structure attendue
                    if "indicators" in data and isinstance(data["indicators"], list):
                        print(f"✅ JSON valide trouvé avec {len(data['indicators'])} indicateurs")
                        print(f"🤖 Le LLM a filtré et retourné {len(data['indicators'])} lois pertinentes pour Hutchinson")
                        return data
                    else:
                        print(f"⚠️  JSON sans structure 'indicators' attendue")

            # Si le parsing échoue, retourner une structure vide
            print("❌ Parsing JSON échoué - structure par défaut")
            return {
                "indicators": [],
                "error": "Impossible de parser la réponse LLM"
            }

        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
            return {
                "indicators": [],
                "error": f"Réponse LLM non valide (JSON): {str(e)}"
            }
        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            return {
                "indicators": [],
                "error": f"Erreur extraction: {str(e)}"
            }

    def get_ui_ready_data(self, company_profile, specific_query=None):
        """
        MÉTHODE PRINCIPALE pour obtenir les données prêtes pour l'UI
        Retourne directement les données JSON que vous voulez afficher
        """
        print("🦙 Analyse LLM pour interface utilisateur...")

        # Obtenir le rapport de base (limité à 2 réglementations)
        base_report = self.get_regulatory_risk_assessment(company_profile, specific_query)

        if "error" in base_report:
            return {
                "indicators": [],
                "error": base_report["error"]
            }

        # Générer l'analyse LLM (retourne du JSON)
        llm_response = self.generate_llm_analysis(base_report, company_profile)

        # Extraire les données UI du LLM
        ui_data = self.extract_ui_data_from_llm_response(llm_response)

        # Ajouter des métadonnées utiles
        ui_data["metadata"] = {
            "company_name": company_profile.get('nom', 'Entreprise'),
            "analysis_date": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "total_indicators": len(ui_data.get("indicators", [])),
            "llm_used": True,
            "model": "llama2"
        }

        # Sauvegarder les résultats dans la collection risk_analysis
        self.save_analysis_to_risk_collection(ui_data, company_profile, specific_query)

        return ui_data

    def save_analysis_to_risk_collection(self, ui_data, company_profile, query):
        """
        Sauvegarde les résultats de l'analyse LLM dans la collection risk_analysis
        """
        try:
            from db import db
            risk_analysis = db["risk_analysis"]

            # Préparer le document à sauvegarder
            analysis_document = {
                "company_name": company_profile.get('nom', 'Hutchinson'),
                "analysis_timestamp": datetime.now(),
                "query_used": query,
                "llm_model": "llama2",
                "total_regulations_analyzed": ui_data["metadata"]["total_indicators"],
                "analysis_results": ui_data["indicators"],
                "metadata": ui_data["metadata"],
                "company_profile_snapshot": {
                    "secteur": company_profile.get('secteur'),
                    "presence_geographique": company_profile.get('presence_geographique', []),
                    "matieres_premieres": company_profile.get('matieres_premieres', [])
                },
                "status": "completed",
                "created_at": datetime.now()
            }

            # Calculer des statistiques pour la sauvegarde
            if ui_data.get("indicators"):
                indicators = ui_data["indicators"]
                analysis_document["analysis_summary"] = {
                    "total_laws_identified": len(indicators),
                    "avg_financial_impact": sum(law.get('impact_financial', 0) for law in indicators) / len(indicators),
                    "avg_reputation_impact": sum(law.get('impact_reputation', 0) for law in indicators) / len(indicators),
                    "avg_operational_impact": sum(law.get('impact_operational', 0) for law in indicators) / len(indicators),
                    "high_impact_laws": len([law for law in indicators if law.get('impact_financial', 0) >= 8]),
                    "laws_with_deadlines": len([law for law in indicators if law.get('deadline') and law.get('deadline') != 'Non définie'])
                }

            # Insérer dans la collection
            result = risk_analysis.insert_one(analysis_document)
            print(f"💾 Analyse sauvegardée dans risk_analysis: {result.inserted_id}")

        except Exception as e:
            print(f"⚠️ Erreur sauvegarde risk_analysis: {e}")
            # Ne pas faire échouer l'analyse si la sauvegarde échoue

def get_hutchinson_profile():
    """
    Récupère le profil Hutchinson depuis la collection MongoDB
    """
    try:
        from db import db
        hutchinson_data = db.hutchinson.find_one()

        if hutchinson_data:
            return hutchinson_data
        else:
            # Profil par défaut si pas trouvé dans la collection
            return {
                "nom": "Hutchinson",
                "secteur": "automobile aerospace manufacturing industrie",
                "presence_geographique": [
                    "France", "Allemagne", "États-Unis", "Chine",
                    "Brésil", "Inde", "Mexique", "Royaume-Uni"
                ],
                "matieres_premieres": [
                    "caoutchouc", "polymères", "métaux", "acier",
                    "aluminium", "silicone", "élastomères"
                ],
                "fournisseurs_regions": [
                    "Asie", "Europe", "Amérique du Nord", "Amérique du Sud"
                ],
                "clients_regions": [
                    "Europe", "Amérique du Nord", "Asie", "Constructeurs automobiles"
                ],
                "secteurs_clients": [
                    "automobile", "aéronautique", "défense", "industrie"
                ]
            }
    except Exception as e:
        print(f"Erreur récupération profil Hutchinson: {e}")
        return None

def interactive_risk_consultant():
    """Interface interactive pour consultation de risques réglementaires"""

    print("🏢 ANALYSE HUTCHINSON - RISQUES RÉGLEMENTAIRES")
    print("=" * 60)

    # Récupérer automatiquement le profil Hutchinson
    print("🔍 Récupération du profil Hutchinson...")
    company_profile = get_hutchinson_profile()

    if not company_profile:
        print("❌ Impossible de récupérer le profil Hutchinson")
        return

    print(f"✅ Profil Hutchinson chargé")
    print(f"   • Secteurs: {company_profile.get('secteur', 'Non défini')}")
    print(f"   • Pays: {', '.join(company_profile.get('presence_geographique', [])[:4])}...")
    print(f"   • Matières: {', '.join(company_profile.get('matieres_premieres', [])[:4])}...")

    # Sélection du mode LLM
    print("\n🤖 MODE D'ANALYSE:")
    print("1. Analyse standard (rapide)")
    print("2. Analyse avec LLM Ollama (recommandé)")
    print("3. Analyse avec règles avancées")

    mode = input("\nChoisissez le mode (1-3, défaut=2): ").strip()
    if not mode:
        mode = "2"

    use_llm = mode == "2"

    rag = RegulatoryRiskRAGWithLLM("ollama" if use_llm else "rules")

    # Question spécifique (optionnelle)
    specific_query = input("\nQuestion spécifique (optionnel): ").strip()
    if not specific_query:
        specific_query = "réglementations automobile aéronautique caoutchouc polymères manufacturing"

    print("\n" + "="*60)
    print("🔍 ANALYSE EN COURS...")
    print(f"🏢 Entreprise: {company_profile['nom']}")
    print(f"🤖 Mode: {'LLM Ollama' if use_llm else 'Standard'}")

    try:
        if use_llm:
            # Utiliser la méthode UI pour avoir les données structurées
            ui_data = rag.get_ui_ready_data(company_profile, specific_query)

            if "error" in ui_data:
                print(f"❌ Erreur: {ui_data['error']}")
                return

            # Afficher les résultats
            metadata = ui_data.get("metadata", {})
            indicators = ui_data.get("indicators", [])

            print("\n📊 RÉSULTATS HUTCHINSON:")
            print("=" * 40)
            print(f"📅 Date: {metadata.get('analysis_date')}")
            print(f"🤖 Modèle: {metadata.get('model')}")
            print(f"📈 Lois identifiées: {len(indicators)}")

            if indicators:
                print("\n🚨 LOIS QUI IMPACTENT HUTCHINSON:")
                print("-" * 50)

                for i, law in enumerate(indicators, 1):
                    print(f"\n{i}. 📜 {law.get('law_name', 'Nom non disponible')}")
                    print(f"   🔗 URL: {law.get('law_url', 'Non disponible')}")
                    print(f"   📅 Échéance: {law.get('deadline', 'Non définie')}")
                    print(f"   💰 Impact financier: {law.get('impact_financial', 0)}/10")
                    print(f"   🎯 Impact réputation: {law.get('impact_reputation', 0)}/10")
                    print(f"   ⚙️  Impact opérationnel: {law.get('impact_operational', 0)}/10")
                    print(f"   📝 Notes: {law.get('notes', 'Aucune note')}")

            # Sauvegarder les données UI
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hutchinson_ui_data_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ui_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Données UI sauvegardées: {filename}")

        else:
            # Mode standard
            report = rag.get_comprehensive_risk_assessment(
                company_profile,
                specific_query,
                use_llm=False
            )

            formatted_report = rag.format_comprehensive_report(report)
            print(formatted_report)

            # Sauvegarder le rapport standard
            filename = f"hutchinson_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            print(f"\n💾 Rapport sauvegardé: {filename}")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()

def launch_hutchinson_analysis():
    """
    Lance directement l'analyse Hutchinson sans questions interactives
    """
    print("🏢 ANALYSE HUTCHINSON - SYSTÈME AUTOMATIQUE")
    print("=" * 60)

    # Récupérer automatiquement le profil Hutchinson
    print("🔍 Récupération du profil Hutchinson depuis la collection...")
    company_profile = get_hutchinson_profile()

    if not company_profile:
        print("❌ Impossible de récupérer le profil Hutchinson")
        return

    print(f"✅ Profil Hutchinson chargé")
    print(f"   • Secteurs: {company_profile.get('secteur', 'Non défini')}")
    print(f"   • Pays: {', '.join(company_profile.get('presence_geographique', [])[:4])}...")
    print(f"   • Matières: {', '.join(company_profile.get('matieres_premieres', [])[:4])}...")

    # Configuration automatique : mode LLM Ollama
    print("\n🤖 Configuration: Analyse LLM Ollama (mode automatique)")

    rag = RegulatoryRiskRAGWithLLM("ollama")

    # Requête automatique basée sur le profil Hutchinson
    specific_query = "réglementations automobile aéronautique caoutchouc polymères manufacturing industrie"

    print("\n" + "="*60)
    print("🔍 ANALYSE EN COURS...")
    print(f"🏢 Entreprise: {company_profile.get('nom', 'Hutchinson')}")  # Utiliser .get() avec valeur par défaut
    print(f"🤖 Mode: LLM Ollama")
    print(f"🔍 Requête: {specific_query}")

    try:
        # Lancement de l'analyse LLM directe
        ui_data = rag.get_ui_ready_data(company_profile, specific_query)

        if "error" in ui_data:
            print(f"❌ Erreur: {ui_data['error']}")
            return

        # Affichage des résultats
        metadata = ui_data.get("metadata", {})
        indicators = ui_data.get("indicators", [])

        print("\n📊 RÉSULTATS HUTCHINSON:")
        print("=" * 40)
        print(f"📅 Date: {metadata.get('analysis_date')}")
        print(f"🤖 Modèle: {metadata.get('model')}")
        print(f"📈 Lois identifiées: {len(indicators)}")

        if indicators:
            print("\n🚨 LOIS QUI IMPACTENT HUTCHINSON:")
            print("-" * 50)

            for i, law in enumerate(indicators, 1):
                print(f"\n{i}. 📜 {law.get('law_name', 'Nom non disponible')}")
                print(f"   🔗 URL: {law.get('law_url', 'Non disponible')}")
                print(f"   📅 Échéance: {law.get('deadline', 'Non définie')}")
                print(f"   💰 Impact financier: {law.get('impact_financial', 0)}/10")
                print(f"   🎯 Impact réputation: {law.get('impact_reputation', 0)}/10")
                print(f"   ⚙️  Impact opérationnel: {law.get('impact_operational', 0)}/10")
                print(f"   📝 Notes: {law.get('notes', 'Aucune note')}")

            # Calcul des moyennes d'impact
            total_laws = len(indicators)
            avg_financial = sum(law.get('impact_financial', 0) for law in indicators) / total_laws
            avg_reputation = sum(law.get('impact_reputation', 0) for law in indicators) / total_laws
            avg_operational = sum(law.get('impact_operational', 0) for law in indicators) / total_laws

            print(f"\n📊 SYNTHÈSE GLOBALE:")
            print(f"   💰 Impact financier moyen: {avg_financial:.1f}/10")
            print(f"   🎯 Impact réputation moyen: {avg_reputation:.1f}/10")
            print(f"   ⚙️  Impact opérationnel moyen: {avg_operational:.1f}/10")

            # Niveau d'alerte global
            global_impact = (avg_financial + avg_reputation + avg_operational) / 3
            if global_impact >= 7:
                alert_level = "🔴 CRITIQUE"
            elif global_impact >= 5:
                alert_level = "🟠 ÉLEVÉ"
            elif global_impact >= 3:
                alert_level = "🟡 MODÉRÉ"
            else:
                alert_level = "🟢 FAIBLE"

            print(f"   🚨 Niveau d'alerte: {alert_level} ({global_impact:.1f}/10)")
        else:
            print("\nℹ️  Aucune loi identifiée comme impactante pour Hutchinson")

        # Sauvegarder les données UI
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"hutchinson_analysis_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(ui_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Données sauvegardées: {filename}")

        # Affichage des données JSON brutes pour debug
        print(f"\n🔧 DONNÉES JSON GÉNÉRÉES:")
        print("-" * 30)
        print(json.dumps(ui_data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch_hutchinson_analysis()
