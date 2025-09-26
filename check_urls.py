#!/usr/bin/env python3
"""
Vérification des URLs dans la collection regulations
"""

from db import db
import json

def check_regulation_urls():
    """Vérifie les URLs disponibles dans vos réglementations"""

    print("🔍 VÉRIFICATION DES URLs DANS LA COLLECTION REGULATIONS")
    print("=" * 60)

    try:
        regulations = list(db.regulations.find())

        print(f"📊 Nombre de réglementations: {len(regulations)}")
        print()

        for i, reg in enumerate(regulations, 1):
            print(f"{i}. {reg.get('nom_loi', reg.get('titre', 'Sans nom'))}")
            print(f"   ID: {reg.get('_id')}")

            # Vérifier tous les champs possibles pour les URLs
            url_fields = ['lien_loi', 'url', 'law_url', 'link', 'source_url', 'reference_url']
            found_urls = {}

            for field in url_fields:
                if field in reg and reg[field]:
                    found_urls[field] = reg[field]

            if found_urls:
                print(f"   🔗 URLs trouvées:")
                for field, url in found_urls.items():
                    print(f"      • {field}: {url}")
            else:
                print(f"   ❌ Aucune URL trouvée")

            # Afficher tous les champs disponibles pour debug
            print(f"   📋 Champs disponibles: {list(reg.keys())}")
            print()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_regulation_urls()
