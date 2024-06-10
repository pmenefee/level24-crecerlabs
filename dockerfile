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

# Create a non-root user to use audio
RUN useradd -ms /bin/bash audiouser

# Add the user to the audio group
RUN usermod -aG audio audiouser

# Switch to the non-root user
USER audiouser

# Create a directory for the application
WORKDIR /code

# Install Python dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt --progress-bar=on

COPY --chown=myuser:myuser ./app ./app

ENV PYTHONPATH /code/app

# Ensure the local bin is in PATH
ENV PATH="/home/audiouser/.local/bin:${PATH}"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]