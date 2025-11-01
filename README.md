## Spirit Voice

A FastAPI-based voice API application.

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
APP_NAME=Spirit Voice API
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### Running with Docker Compose

1. **Build and start the application:**
```bash
docker-compose up --build
```

2. **Run in detached mode:**
```bash
docker-compose up -d
```

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop the application:**
```bash
docker-compose down
```

### Building the Docker Image Manually

```bash
docker build -t spirit_voice_api .
```

### Running the Container Manually

```bash
docker run -p 8000:8000 \
  -e APP_NAME="Spirit Voice API" \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e DEBUG=false \
  spirit_voice_api
```

### Development

The docker-compose.yml includes a volume mount for hot-reloading during development. To enable auto-reload, update the CMD in the Dockerfile or docker-compose command to:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment

For production:
1. Remove the volume mount in docker-compose.yml
2. Set appropriate environment variables
3. Consider using a production-grade WSGI server configuration

## Local Development (without Docker)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
Create a `.env` file with the required variables.

3. **Run the application:**
```bash
python -m uvicorn app.main:app --reload
```