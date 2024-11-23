from py2neo import Graph

def setup_neo4j():
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

    # Criar índices ou carregar dados de filmes e ratings para o grafo
    graph.run("CREATE INDEX ON :Movie(movieId)")
    graph.run("CREATE INDEX ON :User(userId)")

setup_neo4j()
