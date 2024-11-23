from kafka import KafkaProducer
import json

def send_rating_to_kafka(rating_data):
    producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    producer.send('ratings_topic', value=rating_data)
    print("Avaliação enviada para o Kafka")

rating_data = {
    'userId': 1,
    'movieId': 101,
    'rating': 4.5
}
send_rating_to_kafka(rating_data)
