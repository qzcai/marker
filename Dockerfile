# Use Python 3.10
FROM python:3.10-slim
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y build-essential lsb-release sudo wget

# Run install scripts
COPY scripts/install scripts/install
RUN chmod +x scripts/install/tesseract_5_install.sh
RUN chmod +x scripts/install/ghostscript_install.sh
RUN ./scripts/install/tesseract_5_install.sh
RUN ./scripts/install/ghostscript_install.sh
RUN cat scripts/install/apt-requirements.txt | xargs apt-get install -y

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --without dev --no-root

# Configure Flask
COPY . .
EXPOSE 80
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80
CMD ["flask", "run"]
