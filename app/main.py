from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import Product, Webhook
from .tasks import process_csv_import, celery_app
import shutil
import uuid
import os


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Acme Product Importer")


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}.csv"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    
    task = process_csv_import.delay(file_path)
    return {"task_id": task.id}

@app.get("/api/upload/status/{task_id}")
def get_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        return {"state": "PENDING", "percent": 0}
    elif task_result.state == 'PROGRESS':
        return {"state": "PROGRESS", "percent": task_result.info.get('percent', 0)}
    elif task_result.state == 'SUCCESS':
        return {"state": "SUCCESS", "percent": 100, "result": task_result.result}
    else:
        return {"state": "FAILURE", "error": str(task_result.info)}


@app.get("/api/products")
def get_products(
    page: int = 1, 
    search: str = "", 
    db: Session = Depends(get_db)
):
    limit = 20
    offset = (page - 1) * limit
    query = db.query(Product)
    
    if search:
        query = query.filter(Product.sku.contains(search.lower()) | Product.name.contains(search))
        
    products = query.offset(offset).limit(limit).all()
    total = query.count()
    return {"data": products, "total": total, "page": page}


@app.delete("/api/products/all")
def delete_all_products(db: Session = Depends(get_db)):
    db.query(Product).delete()
    db.commit()
    return {"message": "All products deleted"}


@app.post("/api/webhooks")
def create_webhook(url: str, db: Session = Depends(get_db)):
    hook = Webhook(url=url)
    db.add(hook)
    db.commit()
    return {"message": "Webhook added"}

@app.get("/api/webhooks")
def list_webhooks(db: Session = Depends(get_db)):
    return db.query(Webhook).all()