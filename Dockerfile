FROM ubuntu:22.04

# Instala dependências necessárias
RUN apt-get update && apt-get install -y python3 python3-pip

# Copia o arquivo requirements.txt para o contêiner
COPY requirements.txt /tmp/

# Instala as dependências do Python usando o pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copia a aplicação para o contêiner
COPY . .

# Configura a variável de ambiente para especificar o arquivo de aplicação Flask
ENV FLASK_APP=apigtp.py
ENV OPENAI_API_KEY=SUA API AQUI
# Expõe a porta 5000
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
