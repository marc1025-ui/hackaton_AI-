from vector_search import search_similar_regulations
from db import db
import json
from datetime import datetime

def get_hutchinson_profile():
    """Récupère le profil Hutchinson depuis la base"""
    hutchinson = db["hutchinson"]
    profile = hutchinson.find_one({})
    return profile

def create_analysis_prompt(query, regulations, hutchinson_profile):
    """
    Crée un prompt intelligent pour que le LLM analyse les réglementations
    de manière autonome pour Hutchinson
    """

    # Construire le contexte Hutchinson
    hutchinson_context = f"""
PROFIL ENTREPRISE - HUTCHINSON:
- Nom: {hutchinson_profile['company_info']['name']}
- Secteurs: {', '.join(hutchinson_profile['company_info']['sectors'])}
- Siège: {hutchinson_profile['company_info']['headquarters']}
- Activité principale: {hutchinson_profile['company_info']['main_business']}

Présence géographique: {', '.join(hutchinson_profile['geographical_presence'])}

Activités par secteur:
"""

    for sector, activities in hutchinson_profile['business_activities'].items():
        hutchinson_context += f"- {sector}: {', '.join(activities)}\n"

    hutchinson_context += f"\nMatériaux utilisés: {', '.join(hutchinson_profile['typical_materials'])}"
    hutchinson_context += f"\nProduits spécifiques: {', '.join(hutchinson_profile['specific_products'])}"

    # Construire le contexte des réglementations trouvées
    regulations_context = ""
    for i, reg in enumerate(regulations, 1):
        regulations_context += f"""
RÉGLEMENTATION {i}:
ID: {reg.get('id_loi', 'N/A')}
Titre: {reg.get('nom_loi', 'N/A')}
Type: {reg.get('type', 'N/A')}
Lien: {reg.get('lien_loi', 'N/A')}
Date publication: {reg.get('date_publication', 'N/A')}
Pays concernés: {reg.get('pays_concernes', [])}
Score de similarité: {reg.get('score', 0):.4f}

Contenu:
{reg.get('texte', '')[:1500]}...

---
"""

    # Prompt principal pour le LLM
    prompt = f"""Tu es un expert en conformité réglementaire spécialisé dans l'analyse d'impact pour les entreprises industrielles.

{hutchinson_context}

QUESTION DE L'UTILISATEUR: "{query}"

RÉGLEMENTATIONS TROUVÉES PAR RECHERCHE VECTORIELLE:
{regulations_context}

MISSION:
Analyse ces réglementations et détermine leur impact sur Hutchinson. Pour chaque réglementation, évalue:

1. PERTINENCE (0-10): Cette réglementation concerne-t-elle vraiment les activités de Hutchinson ?
   - 0-3: Pas du tout pertinente (ex: pharmaceutique, banque)
   - 4-6: Moyennement pertinente 
   - 7-10: Très pertinente (secteurs auto/aéro, matériaux, étanchéité, vibration)

2. IMPACT GÉOGRAPHIQUE: Quels sites Hutchinson sont concernés ?

3. IMPACT MÉTIER: Quels secteurs/produits/matériaux Hutchinson sont impactés ?

4. SANCTIONS: Quelles sont les sanctions prévues (amendes, prison, suspension) ?

5. SCORE DE RISQUE (0-100): Niveau de risque global pour Hutchinson
   - 0-30: FAIBLE
   - 31-60: MOYEN  
   - 61-80: ÉLEVÉ
   - 81-100: CRITIQUE

6. RECOMMANDATIONS: Actions prioritaires à prendre

FORMAT DE RÉPONSE:
Pour chaque réglementation, structure ta réponse ainsi:

## RÉGLEMENTATION [ID]: [Titre]
**Pertinence:** [0-10] - [Explication]
**Impact géographique:** [Liste des pays/sites concernés]
**Impact métier:** [Secteurs/produits/matériaux impactés]
**Sanctions détectées:** [Liste des sanctions avec montants]
**Score de risque:** [0-100] - Niveau [FAIBLE/MOYEN/ÉLEVÉ/CRITIQUE]
**Recommandations:** [Actions prioritaires]

SYNTHÈSE GLOBALE:
- Nombre total de réglementations analysées: [X]
- Réglementations critiques (score > 80): [X] 
- Réglementations à haut risque (score 61-80): [X]
- Actions prioritaires immédiates: [Liste]

Sois précis, factuel et base-toi uniquement sur les informations fournies."""

    return prompt

def analyze_regulations_with_llm(query, use_local_llm=True):
    """
    Analyse complète des réglementations avec LLM autonome

    Args:
        query (str): Question de l'utilisateur
        use_local_llm (bool): Utiliser Ollama local ou API externe
    """

    print(f"🔍 Recherche de réglementations pour: '{query}'")

    # ÉTAPE 1: Récupération via recherche vectorielle
    regulations = search_similar_regulations(query, limit=5)

    if not regulations:
        return "❌ Aucune réglementation pertinente trouvée."

    print(f"✅ {len(regulations)} réglementations trouvées")

    # ÉTAPE 2: Récupérer le profil Hutchinson
    hutchinson_profile = get_hutchinson_profile()
    if not hutchinson_profile:
        return "❌ Profil Hutchinson non trouvé dans la base de données."

    # ÉTAPE 3: Créer le prompt intelligent
    prompt = create_analysis_prompt(query, regulations, hutchinson_profile)

    print("🤖 Génération de l'analyse par le LLM...")

    # ÉTAPE 4: Appeler le LLM
    if use_local_llm:
        analysis = call_ollama_llm(prompt)
    else:
        analysis = call_openai_llm(prompt)

    return analysis

def call_ollama_llm(prompt):
    """Appelle Ollama en local"""
    try:
        import requests

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",  # ou llama3.1, mistral, etc.
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Plus factuel
                    "top_p": 0.9
                }
            },
            timeout=120  # 2 minutes max
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Erreur: pas de réponse du LLM")
        else:
            return f"❌ Erreur Ollama: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"❌ Erreur de connexion Ollama: {e}\n💡 Assurez-vous qu'Ollama est démarré avec: ollama serve"
    except Exception as e:
        return f"❌ Erreur: {e}"

def call_openai_llm(prompt):
    """Appelle OpenAI API (nécessite clé API)"""
    try:
        import openai
        import os

        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            return "❌ Clé API OpenAI non configurée. Définissez OPENAI_API_KEY."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un expert en conformité réglementaire."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur OpenAI: {e}"

def interactive_regulatory_consultant():
    """Interface interactive pour consultation réglementaire avec LLM"""

    print("🤖 CONSULTANT IA RÉGLEMENTAIRE - HUTCHINSON")
    print("🔋 Alimenté par recherche vectorielle + LLM autonome")
    print("=" * 60)

    print("Choisissez votre LLM:")
    print("1. Ollama (local, gratuit)")
    print("2. OpenAI GPT-4 (API, payant)")

    while True:
        choice = input("Votre choix (1 ou 2): ").strip()
        if choice in ["1", "2"]:
            use_local = (choice == "1")
            break
        print("❌ Veuillez choisir 1 ou 2")

    llm_name = "Ollama" if use_local else "OpenAI GPT-4"
    print(f"✅ LLM sélectionné: {llm_name}")
    print("\n💡 Exemples de questions:")
    print("- 'réglementations automobiles étanchéité'")
    print("- 'sanctions aérospatiale vibration'")
    print("- 'CBAM émissions carbone'")
    print("- 'réglementations matériaux caoutchouc'")
    print("\n💡 Tapez 'quit' pour quitter")
    print("=" * 60)

    while True:
        query = input("\n❓ Votre question: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Au revoir !")
            break

        if not query:
            continue

        print("\n" + "⏳" * 20)
        print("🔄 Analyse en cours...")

        try:
            analysis = analyze_regulations_with_llm(query, use_local_llm=use_local)

            print("\n" + "=" * 80)
            print("📄 RAPPORT D'ANALYSE RÉGLEMENTAIRE")
            print("=" * 80)
            print(analysis)
            print("=" * 80)

            # Sauvegarder le rapport
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rapport_reglementaire_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"RAPPORT D'ANALYSE RÉGLEMENTAIRE - {datetime.now()}\n")
                f.write(f"Question: {query}\n")
                f.write("=" * 80 + "\n")
                f.write(analysis)

            print(f"💾 Rapport sauvegardé: {filename}")

        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")

if __name__ == "__main__":
    # Test rapide
    print("🧪 Test du système RAG + LLM")
    test_query = "réglementations automobiles systèmes étanchéité"

    # Version simple pour test (sans LLM)
    regulations = search_similar_regulations(test_query, limit=3)
    print(f"✅ Test recherche vectorielle: {len(regulations)} résultats")

    # Lancer l'interface interactive
    print("\n🚀 Lancement de l'interface interactive...")
    interactive_regulatory_consultant()
