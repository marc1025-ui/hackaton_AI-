from sentence_transformers import SentenceTransformer
from db import db
import numpy as np

# Modèle d'embedding (même que celui utilisé pour créer les embeddings)
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar_regulations(query_text, limit=5):
    """
    Recherche les réglementations similaires à une requête textuelle

    Args:
        query_text (str): Texte de la requête
        limit (int): Nombre de résultats à retourner

    Returns:
        list: Liste des réglementations similaires
    """
    regulations = db["regulations"]

    # Créer l'embedding de la requête
    query_embedding = model.encode(query_text).tolist()

    # Pipeline d'agrégation pour la recherche vectorielle
    # IMPORTANT: Le nom de l'index doit correspondre à celui dans Atlas
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index_1",  # Nom mis à jour de votre index
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,  # Nombre de candidats à examiner
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
                "score": {"$meta": "vectorSearchScore"}  # Score de similarité
            }
        }
    ]

    try:
        results = list(regulations.aggregate(pipeline))
        return results
    except Exception as e:
        print(f"❌ Erreur lors de la recherche vectorielle : {e}")
        print("💡 Vérifiez le nom de l'index vectoriel dans Atlas")
        return []

def print_search_results(results, query):
    """Affiche les résultats de recherche de manière formatée"""
    print(f"\n🔍 Résultats pour la requête : '{query}'")
    print("=" * 60)

    if not results:
        print("❌ Aucun résultat trouvé")
        return

    for i, result in enumerate(results, 1):
        score = result.get('score', 0)
        print(f"\n📄 Résultat {i} (Score: {score:.4f})")
        print(f"📋 ID Loi: {result.get('id_loi', 'N/A')}")
        print(f"📝 Titre: {result.get('titre', 'N/A')}")
        print(f"📅 Date: {result.get('date_promulgation', 'N/A')}")

        # Afficher les premiers mots du texte
        texte = result.get('texte', '')
        if len(texte) > 200:
            texte = texte[:200] + "..."
        print(f"📖 Extrait: {texte}")
        print("-" * 40)

def interactive_search():
    """Mode de recherche interactif"""
    print("🤖 Moteur de recherche de réglementations par similarité sémantique")
    print("💡 Tapez 'quit' pour quitter")
    print("=" * 60)

    while True:
        query = input("\n🔍 Entrez votre recherche : ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Au revoir !")
            break

        if not query:
            continue

        print("⏳ Recherche en cours...")
        results = search_similar_regulations(query, limit=3)
        print_search_results(results, query)

if __name__ == "__main__":
    # Test avec une requête d'exemple
    test_query = "droit du travail"
    print("🧪 Test de recherche vectorielle...")
    results = search_similar_regulations(test_query, limit=3)
    print_search_results(results, test_query)

    # Mode interactif
    print("\n" + "="*60)
    interactive_search()
