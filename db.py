from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://marcjuniorh29:qTdh0MSrMZRkLM2l@clustermarc.os3r2.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMarc"

client = MongoClient(CONNECTION_STRING)
db = client["hackathon_regulations"]