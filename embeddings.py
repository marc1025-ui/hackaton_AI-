from datetime import datetime
from sentence_transformers import SentenceTransformer
from db import db  # <--- on importe la connexion propre

# Modèle d'embedding (384 dimensions)
model = SentenceTransformer("all-MiniLM-L6-v2")

def add_embeddings():
    """Ajoute un embedding pour chaque loi qui n’en a pas encore"""
    regulations = db["regulations"]
    for doc in regulations.find({"embedding": {"$exists": False}}):
        emb = model.encode(doc["texte"]).tolist()
        regulations.update_one({"_id": doc["_id"]}, {"$set": {"embedding": emb}})
        print(f"✅ Embedding ajouté pour {doc['id_loi']}")

if __name__ == "__main__":
    add_embeddings()