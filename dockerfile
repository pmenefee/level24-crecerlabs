FROM python:3.10

## Install non-pip requirements.
RUN pip install pipwin
RUN apt-get update && apt-get install -y portaudio19-dev libsndfile1-dev

# Update pip to the latest version.
RUN pip install --upgrade pip

# Install pip requirements.
WORKDIR /code
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application to the container.
COPY ./src ./src

# Setup services
# CMD ["uvicorn", "src.main:app","-host","0.0.0.0","--port","80","--reload"]
# CMD ["mongodb","-p","27017:27017","-d","mongo/mongo-express"]
