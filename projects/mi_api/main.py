from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="mi_api",
    description="API generada por J.A.R.V.I.S.",
    version="1.0.0"
)

# Modelos
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    created_at: Optional[str] = None

# Base de datos en memoria
items_db = []

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a mi_api",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "items_count": len(items_db)
    }

@app.get("/api/items", response_model=List[Item])
async def list_items():
    """Listar todos los items"""
    return items_db

@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    """Obtener item por ID"""
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post("/api/items", response_model=Item)
async def create_item(item: Item):
    """Crear nuevo item"""
    item.id = len(items_db) + 1
    item.created_at = datetime.now().isoformat()
    items_db.append(item.dict())
    return item

@app.put("/api/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """Actualizar item"""
    for i, existing in enumerate(items_db):
        if existing["id"] == item_id:
            items_db[i] = {**item.dict(), "id": item_id}
            return items_db[i]
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    """Eliminar item"""
    for i, existing in enumerate(items_db):
        if existing["id"] == item_id:
            return items_db.pop(i)
    raise HTTPException(status_code=404, detail="Item no encontrado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
