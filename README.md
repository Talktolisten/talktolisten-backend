# Talk To Listen Back End Development (Dev Guide)

- Microservice for Talk To Listen project

## Installation

1. Create a virtual environment

```bash
python -m venv venv
```

2. Activate the virtual environment

**MacOS/Linux**:

```bash
source venv/bin/activate
```

**Windows**:

```bash
venv\Scripts\activate
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Run the server (for development only)

```bash
uvicorn app.main:app --reload
```

or

```bash
python3 server.py
```

## Migration with Alembic

1. Update database using

```bash
alembic revision --autogenerate -m "Commit message"
```

then

```bash
alembic upgrade head
```

## Run tests

```bash
pytest -v -s
```

## Docker build and run

1. Build

```bash
docker build -t ttl-backend .
```

2. Run

```bash
docker run --env-file .env -p 8000:8000 ttl-backend
```

## GitHub Action Runner starts on EC2

```bash
nohup ./run.sh &
```
