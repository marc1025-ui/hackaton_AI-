from db import db

def check_mongodb_status():
    """Vérifie l'état de la base de données et des embeddings"""

    print("🔍 Vérification de l'état de MongoDB...")

    try:
        regulations = db["regulations"]

        # Compter le total de documents
        total_docs = regulations.count_documents({})
        print(f"📊 Total de documents dans 'regulations': {total_docs}")

        # Compter ceux avec embeddings
        docs_with_embeddings = regulations.count_documents({"embedding": {"$exists": True}})
        print(f"🧠 Documents avec embeddings: {docs_with_embeddings}")

        # Échantillon de documents
        print("\n📋 Échantillon de documents:")
        sample_docs = list(regulations.find().limit(3))

        for i, doc in enumerate(sample_docs, 1):
            print(f"\n{i}. ID: {doc.get('_id')}")
            print(f"   Titre: {doc.get('titre', 'N/A')[:100]}")
            print(f"   A un embedding: {'✅' if 'embedding' in doc else '❌'}")
            if 'embedding' in doc:
                print(f"   Taille embedding: {len(doc['embedding'])} dimensions")

        # Test de recherche simple
        print("\n🔍 Test de recherche simple (sans index vectoriel):")
        simple_search = list(regulations.find({"texte": {"$regex": "droit", "$options": "i"}}).limit(2))
        print(f"Documents contenant 'droit': {len(simple_search)}")

        return total_docs > 0 and docs_with_embeddings > 0

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_vector_search_simple():
    """Test simple de recherche vectorielle"""
    from sentence_transformers import SentenceTransformer

    print("\n🧪 Test de recherche vectorielle...")

    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        regulations = db["regulations"]

        # Créer un embedding de test
        test_query = "droit du travail"
        query_embedding = model.encode(test_query).tolist()
        print(f"✅ Embedding créé pour '{test_query}' ({len(query_embedding)} dimensions)")

        # Tenter la recherche vectorielle
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index_embedding",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 10,
                    "limit": 3
                }
            },
            {
                "$project": {
                    "titre": 1,
                    "id_loi": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        results = list(regulations.aggregate(pipeline))

        if results:
            print(f"✅ Recherche vectorielle réussie! {len(results)} résultats:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('titre', 'N/A')[:50]}... (Score: {result.get('score', 0):.4f})")
        else:
            print("⚠️ Recherche vectorielle sans résultats - l'index n'est peut-être pas encore actif")

    except Exception as e:
        print(f"❌ Erreur lors de la recherche vectorielle: {e}")
        if "index not found" in str(e).lower():
            print("💡 L'index vectoriel n'est pas encore actif. Attendez quelques minutes.")
        return False

    return len(results) > 0

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC DU SYSTÈME RAG")
    print("=" * 50)

    # Vérifier MongoDB
    mongo_ok = check_mongodb_status()

    if mongo_ok:
        print("\n" + "="*50)
        # Tester la recherche vectorielle
        vector_ok = test_vector_search_simple()

        print("\n" + "="*50)
        print("📋 RÉSUMÉ:")
        print(f"🗄️  MongoDB: {'✅ OK' if mongo_ok else '❌ Problème'}")
        print(f"🔍 Recherche vectorielle: {'✅ OK' if vector_ok else '⚠️ Index pas encore actif'}")

        if mongo_ok and vector_ok:
            print("\n🎉 Votre système RAG est prêt à utiliser!")
        elif mongo_ok and not vector_ok:
            print("\n⏳ Attendez quelques minutes que l'index vectoriel soit actif, puis relancez.")

    else:
        print("\n❌ Problème avec MongoDB. Vérifiez votre connexion.")
