FROM python:3.10

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    alsa-utils \
    portaudio19-dev \
    libasound2-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update pip to the latest version
RUN pip install --upgrade pip

# Create a directory for the application
WORKDIR /code

# Install Python dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt --progress-bar=on

COPY ./app ./app

ENV PYTHONPATH /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]