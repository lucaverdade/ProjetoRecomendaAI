# Escolher uma imagem base que já tenha o Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para dentro do container
COPY . /app

# Atualizar pip e instalar dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expor a porta onde o Streamlit irá rodar (por padrão 8501)
EXPOSE 8501

# Definir o comando que será executado ao iniciar o container
CMD ["streamlit", "run", "app.py"]
