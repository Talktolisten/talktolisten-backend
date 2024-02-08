# Talk To Listen Back End

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

## Docker run
```bash
docker run --env-file .env -p 8000:8000 ttl-backend
```