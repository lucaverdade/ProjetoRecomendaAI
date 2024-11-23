# Sistema de Recomendação de Filmes

Este é um sistema de recomendação de filmes baseado no algoritmo **K-Nearest Neighbors (KNN)**. Ele utiliza avaliações de usuários para recomendar filmes semelhantes ao escolhido. O sistema é implementado com **Streamlit**, **MongoDB** para armazenar dados de filmes e avaliações, e **Kafka** para envio assíncrono das avaliações.

## Tecnologias Utilizadas

- **Streamlit**: Framework para construção da interface web.
- **Pandas**: Manipulação de dados.
- **MongoDB**: Banco de dados NoSQL para armazenar filmes e avaliações.
- **Kafka**: Sistema de mensagens assíncronas para enviar as avaliações dos usuários.
- **Scikit-learn**: Para implementar o algoritmo KNN.
- **Docker** (caso esteja usando): Para rodar todos os serviços (Streamlit, MongoDB, Kafka) em contêineres.

## Funcionalidades

- **Recomendação de Filmes**: Com base na avaliação de um filme, o sistema recomenda filmes semelhantes utilizando o algoritmo KNN e a métrica de distância cosseno.
- **Envio de Avaliações**: As avaliações dos usuários são enviadas para um tópico do Kafka, garantindo a escalabilidade e o processamento assíncrono.
- **Interface Intuitiva**: O usuário pode facilmente selecionar um filme, atribuir uma nota e ver as recomendações de filmes.

## Arquitetura

### 1. **Obtenção de Dados**
   O sistema se conecta a um banco de dados **MongoDB**, onde há duas coleções principais:
   - **Filmes**: Contém os filmes e seus títulos.
   - **Avaliações**: Contém as avaliações de filmes feitas pelos usuários.

### 2. **Recomendação**
   Após o usuário selecionar um filme e dar uma nota, o sistema usa o **K-Nearest Neighbors (KNN)** para encontrar os filmes mais semelhantes ao escolhido, baseado nas avaliações feitas por outros usuários. A similaridade é calculada usando a **distância cosseno** entre as avaliações dos filmes.

### 3. **Kafka**
   A avaliação feita pelo usuário é enviada para um tópico Kafka chamado `movie_ratings`, onde pode ser processada por outros serviços ou sistemas de recomendação.

### 4. **Streamlit**
   A interface é criada com **Streamlit**, permitindo uma interação simples onde o usuário pode:
   - Escolher um filme.
   - Avaliar o filme com uma nota de 1 a 5.
   - Receber recomendações baseadas na avaliação.

## Como Executar

### 1. **Pré-requisitos**

- **MongoDB**: Certifique-se de que o MongoDB esteja em execução e que as coleções de filmes e avaliações estejam populadas com dados.
- **Kafka**: O Kafka deve estar em execução para permitir o envio das avaliações.
- **Python**: Instale as dependências utilizando o `pip`:

```bash
pip install streamlit pandas pymongo kafka-python scikit-learn

### Explicações Adicionais

- **MongoDB**: O banco de dados MongoDB armazena os filmes e avaliações. No exemplo acima, os filmes têm uma coleção `movies` e as avaliações são armazenadas na coleção `ratings`.
  
- **Kafka**: O Kafka é utilizado para enviar as avaliações dos usuários de maneira assíncrona, possibilitando uma integração fácil com outros serviços que possam consumir essas informações, como sistemas de análise ou novas recomendações.

- **KNN (K-Nearest Neighbors)**: O KNN é o algoritmo central que utiliza as avaliações dos usuários para encontrar filmes semelhantes. Ele é treinado com uma matriz onde cada linha representa um usuário e cada coluna representa um filme.

Essa estrutura de `README.md` explica de forma clara as funcionalidades, arquitetura e como executar o sistema. Se você precisar ajustar ou expandir algum conteúdo, fique à vontade para personalizar.
