import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
import logging


# Configuração do logging para ajudar na depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_mongo(uri="mongodb://localhost:27017/", db_name="recommendationApp"):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # Definir um timeout de conexão
        client.admin.command('ping')  # Verifica se a conexão foi bem-sucedida
        logging.info(f"Conexão bem-sucedida ao MongoDB no URI {uri}")
        return client[db_name]
    except PyMongoError as e:
        logging.error(f"Erro ao conectar ao MongoDB: {e}")
        return None

def get_movies():
    db = connect_to_mongo()
    if db is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de falha na conexão

    movies_collection = db['movies']
    # Obter todos os filmes da coleção e converter para lista de dicionários
    movies = list(movies_collection.find({}))
    
    if not movies:
        logging.warning("Nenhum filme encontrado na coleção.")
        return pd.DataFrame()  # Retorna um DataFrame vazio caso não haja filmes

    # Criar um DataFrame do pandas a partir da lista de filmes
    movies_df = pd.DataFrame(movies)
    
    # Verificar se a coluna 'title' existe
    if 'title' not in movies_df.columns:
        logging.error("Coluna 'title' não encontrada nos filmes!")
        return pd.DataFrame()  # Retorna um DataFrame vazio se não encontrar a coluna

    return movies_df

def load_movies():
    db = connect_to_mongo()
    if db is None:
        return

    movies_collection = db['movies']
    
    # Carregar os filmes do arquivo CSV
    try:
        movies_df = pd.read_csv('movies.csv')
    except Exception as e:
        logging.error(f"Erro ao carregar o CSV de filmes: {e}")
        return

    # Verificar se a coluna 'title' existe no CSV
    if 'title' not in movies_df.columns:
        logging.error("A coluna 'title' não existe no CSV de filmes.")
        return

    logging.info("A coluna 'title' foi encontrada no CSV de filmes.")

    # Inserir os filmes no MongoDB usando bulk_write para eficiência
    bulk_operations = []
    for index, row in movies_df.iterrows():
        movie_data = row.to_dict()
        logging.info(f"Inserindo filme: {movie_data.get('title')}")

        bulk_operations.append(
            UpdateOne(
                {'movieId': row['movieId']},  # Verifica se o filme já existe pelo ID
                {'$set': movie_data},  # Atualiza ou insere
                upsert=True
            )
        )

    # Executa todas as operações em lote
    if bulk_operations:
        try:
            result = movies_collection.bulk_write(bulk_operations)
            logging.info(f"Inserção em massa concluída. {result.upserted_count} filmes inseridos.")
        except PyMongoError as e:
            logging.error(f"Erro ao inserir filmes: {e}")

def load_ratings():
    db = connect_to_mongo()
    if db is None:
        return

    ratings_collection = db['ratings']

    # Carregar as avaliações do arquivo CSV
    try:
        ratings_df = pd.read_csv('ratings.csv')
    except Exception as e:
        logging.error(f"Erro ao carregar o CSV de avaliações: {e}")
        return

    # Verificar se a coluna 'userId', 'movieId', 'rating' existe no CSV
    if not {'userId', 'movieId', 'rating'}.issubset(ratings_df.columns):
        logging.error("As colunas necessárias ('userId', 'movieId', 'rating') não existem no CSV de avaliações.")
        return

    logging.info("As colunas necessárias foram encontradas no CSV de avaliações.")

    # Inserir as avaliações no MongoDB usando bulk_write para eficiência
    bulk_operations = []
    for index, row in ratings_df.iterrows():
        rating_data = row.to_dict()
        logging.info(f"Inserindo avaliação: {rating_data.get('userId')} - {rating_data.get('movieId')}")

        bulk_operations.append(
            UpdateOne(
                {'userId': row['userId'], 'movieId': row['movieId']},  # Verifica se a avaliação já existe
                {'$set': rating_data},  # Atualiza ou insere
                upsert=True
            )
        )

    # Executa todas as operações em lote
    if bulk_operations:
        try:
            result = ratings_collection.bulk_write(bulk_operations)
            logging.info(f"Inserção em massa concluída. {result.upserted_count} avaliações inseridas.")
        except PyMongoError as e:
            logging.error(f"Erro ao inserir avaliações: {e}")

# Chamar as funções para carregar dados
load_movies()  # Carregar filmes
load_ratings()  # Carregar avaliações
