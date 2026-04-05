# SunMate

A Python API build with FastAPI, with a simple frontend dashboard build with React, to handle solar energy data. 

## Backend

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic pytest
```

1. Installs venv (virtual environment)
2. Activates the virtual environment
3. Install all dependencies

### Running

```bash
uvicorn main:app --reload
```

The API runs at http://localhost:8000

### API Endpoints

- `GET /battery/soc` - Get latest battery soc

- `POST /battery/daily` - Post battery data (array of `{timestamp, soc}`) and get a response back with "lowest_soc", "highest_soc" and "soc_difference"

- `GET /energy/consumption` - Get all energy consumption entries

- `POST /energy/consumption` - Post a consumption entry (`{timestamp, consumption_kwh}`)

### Docs

FastAPI built-in Swagger docs available at http://localhost:8000/docs

### Testing

```bash
pytest
```

## Frontend

The frontend is build with React, and is a very simple showcase of the API's functionality

### Setup

```bash
cd frontend
npm install
```

### Running

```bash
npm run dev
```

The frontend runs at http://localhost:5176/. 
If there is a CORS error, change allow_origins in add_middleware in main.py, to your own localhost. 

