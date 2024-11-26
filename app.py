import streamlit as st
import pandas as pd
from pymongo import MongoClient
from kafka import KafkaProducer
import json
import random  # Para gerar IDs únicos simulados para usuários
from sklearn.neighbors import NearestNeighbors

# Configuração global para MongoDB
MONGO_URI = "mongodb://mongodb:27017/"
DB_NAME = "recommendationApp"

# Função para obter filmes do MongoDB
def get_movies():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        movies_collection = db['movies']
        # Carregar filmes
        movies = list(movies_collection.find({}, {"_id": 0, "movieId": 1, "title": 1}))
        return pd.DataFrame(movies)
    except Exception as e:
        st.error(f"Erro ao carregar filmes do MongoDB: {e}")
        return pd.DataFrame()

# Função para obter avaliações do MongoDB
def get_ratings():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        ratings_collection = db['ratings']
        # Carregar avaliações
        ratings = list(ratings_collection.find({}, {"_id": 0, "userId": 1, "movieId": 1, "rating": 1}))
        return pd.DataFrame(ratings)
    except Exception as e:
        st.error(f"Erro ao carregar avaliações do MongoDB: {e}")
        return pd.DataFrame()

# Função para recomendar filmes com base no KNN
def recommend_movies(user_rating, ratings_df, movies_df):
    try:
        if ratings_df.empty or movies_df.empty:
            st.error("Não há dados suficientes para gerar recomendações.")
            return

        # Criar a matriz de avaliações (usuários x filmes)
        ratings_matrix = ratings_df.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)

        # Adicionar a nova avaliação à matriz
        new_ratings = pd.Series(0, index=ratings_matrix.columns)
        new_ratings[user_rating['movieId']] = user_rating['rating']
        ratings_matrix.loc[len(ratings_matrix)] = new_ratings

        # Modelo KNN
        knn = NearestNeighbors(n_neighbors=6, metric='cosine')
        knn.fit(ratings_matrix.values)

        # Encontrar os vizinhos mais próximos
        distances, indices = knn.kneighbors(ratings_matrix.iloc[-1].values.reshape(1, -1))

        # Filtrar os filmes recomendados
        recommended_movie_ids = ratings_matrix.columns[indices.flatten()[1:]]
        recommended_movies = movies_df[movies_df['movieId'].isin(recommended_movie_ids)]

        if not recommended_movies.empty:
            st.write("### Filmes recomendados:")
            for _, row in recommended_movies.iterrows():
                st.markdown(f"- **{row['title']}**")
        else:
            st.info("Nenhum filme recomendado foi encontrado.")
    except Exception as e:
        st.error(f"Erro ao recomendar filmes: {e}")

# Função para enviar avaliação para o MongoDB e Kafka
def send_rating_to_mongo_and_kafka(movie_title, movie_id, rating):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        ratings_collection = db['ratings']

        # Gerar um ID de usuário aleatório para simular um novo usuário
        user_id = random.randint(100, 10000)  # Reduzindo o número para manter mais rápido

        # Criar o objeto de avaliação
        user_rating = {
            'movieTitle': str(movie_title),
            'movieId': int(movie_id),
            'rating': int(rating),
            'userId': int(user_id)
        }

        # Salvar avaliação no MongoDB
        ratings_collection.insert_one(user_rating)

        # Enviar para o Kafka (conversão de ObjectId para string)
        producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')  # Converte ObjectId para string
        )
        producer.send("movie_ratings", value=user_rating)
        producer.flush()

        st.success(f"Avaliação enviada para o MongoDB e Kafka com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar avaliação para o MongoDB ou Kafka: {e}")

# Streamlit App
st.title('Recomendação de Filmes')

# Carregar filmes e avaliações do MongoDB
movies_df = get_movies()
ratings_df = get_ratings()

if not movies_df.empty:
    # Criar lista de opções para o selectbox
    movie_options = movies_df['title'].tolist()
    selected_movie = st.selectbox('Escolha um filme', movie_options)
    rating = st.slider('Dê uma nota ao filme', min_value=1, max_value=5, step=1)

    # Quando o botão "Enviar Avaliação" for pressionado
    if st.button('Enviar Avaliação'):
        # Obtenha o ID do filme
        movie_id = movies_df[movies_df['title'] == selected_movie].iloc[0]['movieId']
        
        # Enviar avaliação para MongoDB e Kafka
        send_rating_to_mongo_and_kafka(selected_movie, movie_id, rating)

        # Adicionar a avaliação diretamente ao dataframe local
        if not ratings_df.empty:
            user_id = ratings_df['userId'].max() + 1  # Simular novo userId
        else:
            user_id = 1  # Primeiro usuário se o dataframe estiver vazio
        
        new_rating = pd.DataFrame([{'userId': user_id, 'movieId': movie_id, 'rating': rating}])
        ratings_df = pd.concat([ratings_df, new_rating], ignore_index=True)

        # Recalcular e exibir as recomendações
        user_rating = {'movieId': movie_id, 'rating': rating, 'userId': user_id}
        recommend_movies(user_rating, ratings_df, movies_df)
else:
    st.error("Não foi possível carregar os filmes. Verifique o MongoDB.")
