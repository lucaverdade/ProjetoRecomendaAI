from pymongo import MongoClient

# Conectar ao MongoDB (modifique o URI, caso necessário)
client = MongoClient("mongodb://localhost:27017/")  # ou o URI adequado
db = client.recommendationApp  # substitua pelo nome do seu banco
collection = db.movies  # nome da coleção onde estão os filmes

# Recuperar um documento
movie = collection.find_one()
print(movie)
print(db.list_collection_names())
collection.insert_one({"title": "Inception", "year": 2010})
