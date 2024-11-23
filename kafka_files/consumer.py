from kafka import KafkaConsumer
from pymongo import MongoClient
import json

def consume_ratings_from_kafka():
    consumer = KafkaConsumer('ratings_topic', bootstrap_servers='localhost:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    client = MongoClient("mongodb://localhost:27017/")
    db = client['recommendationApp']
    ratings_collection = db['ratings']

    for message in consumer:
        rating_data = message.value
        ratings_collection.update_one(
            {'userId': rating_data['userId'], 'movieId': rating_data['movieId']},
            {'$set': rating_data}, upsert=True
        )
        print(f"Avaliação do usuário {rating_data['userId']} foi salva no MongoDB")

consume_ratings_from_kafka()
