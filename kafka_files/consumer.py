from kafka import KafkaConsumer
from pymongo import MongoClient
import json

from kafka import KafkaConsumer
from pymongo import MongoClient
import json

def consume_ratings():
    try:
        consumer = KafkaConsumer(
            'movie_ratings',
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='movie-rating-consumer-group'
        )
        client = MongoClient("mongodb://mongodb:27017/")
        db = client['recommendationApp']
        ratings_collection = db['ratings']

        for message in consumer:
            user_rating = message.value
            print("Mensagem recebida do Kafka:", user_rating)  # Log para depuração

            # Insira a avaliação no MongoDB
            ratings_collection.insert_one(user_rating)
            print("Avaliação salva no MongoDB:", user_rating)  # Log após salvar
    except Exception as e:
        print(f"Erro ao consumir mensagens do Kafka: {e}")



consume_ratings_from_kafka()
