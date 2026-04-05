# mi_api

API Web construida con FastAPI por J.A.R.V.I.S.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /` - Root
- `GET /api/health` - Health check
- `GET /api/items` - Listar items
- `POST /api/items` - Crear item
