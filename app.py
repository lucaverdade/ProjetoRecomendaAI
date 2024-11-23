import streamlit as st
import pandas as pd
from pymongo import MongoClient
from kafka import KafkaProducer
import json
from sklearn.neighbors import NearestNeighbors
import numpy as np

# Função para obter os filmes do MongoDB
def get_movies():
    try:
        # Conectar ao MongoDB
        client = MongoClient("mongodb://mongodb:27017/")  # Substitua pelo seu endereço MongoDB
        db = client['recommendationApp']
        movies_collection = db['movies']
        
        # Obter todos os filmes da coleção
        movies = list(movies_collection.find({}))
        
        # Verificar se a lista de filmes não está vazia
        if not movies:
            st.error("Nenhum filme encontrado no banco de dados.")
            return pd.DataFrame()
        
        # Criar um DataFrame do pandas a partir dos filmes
        movies_df = pd.DataFrame(movies)
        
        # Verificar se a coluna 'title' existe
        if 'title' in movies_df.columns:
            return movies_df
        else:
            st.error("A coluna 'title' não foi encontrada no banco de dados.")
            return pd.DataFrame()  # Retorna DataFrame vazio
    except Exception as e:
        st.error(f"Erro ao carregar filmes do MongoDB: {e}")
        return pd.DataFrame()

# Função para obter as avaliações do MongoDB
def get_ratings():
    try:
        # Conectar ao MongoDB
        client = MongoClient("mongodb://mongodb:27017/")  # Substitua pelo seu endereço MongoDB
        db = client['recommendationApp']
        ratings_collection = db['ratings']
        
        # Obter todas as avaliações da coleção
        ratings = list(ratings_collection.find({}))
        
        # Verificar se a lista de avaliações não está vazia
        if not ratings:
            st.error("Nenhuma avaliação encontrada no banco de dados.")
            return pd.DataFrame()
        
        # Criar um DataFrame do pandas a partir das avaliações
        ratings_df = pd.DataFrame(ratings)
        
        # Verificar se as colunas essenciais estão presentes
        if 'userId' in ratings_df.columns and 'movieId' in ratings_df.columns and 'rating' in ratings_df.columns:
            return ratings_df
        else:
            st.error("As colunas 'userId', 'movieId' e 'rating' não foram encontradas no banco de dados.")
            return pd.DataFrame()  # Retorna DataFrame vazio
    except Exception as e:
        st.error(f"Erro ao carregar avaliações do MongoDB: {e}")
        return pd.DataFrame()

# Função para recomendar filmes com base no KNN
def recommend_movies(user_rating, ratings_df, movies_df):
    st.write(f"Recomendações para o filme com ID {user_rating['movieId']}")

    # Criar a matriz de avaliações para filmes
    ratings_matrix = ratings_df.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)

    # Ajustar o KNN
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(ratings_matrix.values.T)  # T para transpor para filmes x usuários
    
    # Obter o índice do filme escolhido
    movie_id = user_rating['movieId']
    movie_idx = ratings_matrix.columns.get_loc(movie_id)  # Encontrar o índice do filme

    # Encontrar filmes semelhantes
    distances, indices = knn.kneighbors(ratings_matrix.values.T[movie_idx].reshape(1, -1), n_neighbors=6)
    
    # Obter os IDs dos filmes recomendados (excluindo o filme já escolhido)
    recommended_movie_ids = [ratings_matrix.columns[i] for i in indices.flatten()[1:]]  # Ignorar o próprio filme
    recommended_movies = movies_df[movies_df['movieId'].isin(recommended_movie_ids)]

    if not recommended_movies.empty:
        st.write("Filmes recomendados:")
        for _, row in recommended_movies.iterrows():
            st.markdown(f"### {row['title']}")
    else:
        st.write("Não encontramos filmes similares com base na avaliação.")

# Função para enviar avaliação para o Kafka
def send_rating_to_kafka(user_rating):
    try:
        # Garantir que os tipos sejam serializáveis
        user_rating['movieId'] = int(user_rating['movieId'])
        user_rating['rating'] = int(user_rating['rating'])

        # Configurar o produtor Kafka
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',  # Use o nome do serviço Kafka no Compose
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        producer.send('movie_ratings', value=user_rating)
        producer.flush()
        st.success("Avaliação enviada para o Kafka com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar avaliação para o Kafka: {e}")

# Streamlit App
st.title('Recomendação de Filmes')

# Obter filmes e avaliações
movies_df = get_movies()
ratings_df = get_ratings()

if not movies_df.empty and not ratings_df.empty:
    # Seleção de filmes
    movie_options = movies_df['title'].tolist()
    selected_movie = st.selectbox('Escolha um filme', movie_options)

    # Avaliação do filme com estrelas
    rating = st.slider('Dê uma nota ao filme', min_value=1, max_value=5, step=1)

    # Botão para enviar avaliação
    if st.button('Enviar Avaliação'):
        # Criar o dicionário de avaliação
        user_rating = {'movieTitle': selected_movie, 'rating': rating, 'movieId': movies_df[movies_df['title'] == selected_movie].iloc[0]['movieId']}
        st.write(f"Avaliação registrada: {user_rating}")

        # Enviar para o Kafka
        send_rating_to_kafka(user_rating)

        # Recomendar filmes baseados na avaliação
        recommend_movies(user_rating, ratings_df, movies_df)
else:
    st.error("Não foi possível carregar os filmes ou as avaliações. Verifique o MongoDB.")
