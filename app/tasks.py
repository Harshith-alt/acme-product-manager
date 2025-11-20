import csv
import os
import requests
from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from .database import SessionLocal, engine
from .models import Product, Webhook, Base


REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

celery_app = Celery(
    "worker", 
    broker=REDIS_URL, 
    backend=REDIS_URL
)

@celery_app.task(bind=True)
def process_csv_import(self, file_path):
    db: Session = SessionLocal()
    try:
        total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8')) - 1
    except:
        total_lines = 1

    batch_size = 1000
    batch_dict = {} 
    processed_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                clean_row = {k.lower().strip(): v for k, v in row.items() if k}
                sku = clean_row.get('sku', '').strip().lower()
                
                if not sku:
                    continue

                name = clean_row.get('name', 'Unknown Product')
                desc = clean_row.get('description', '')
                
                batch_dict[sku] = {
                    "sku": sku,
                    "name": name,
                    "description": desc,
                    "is_active": True
                }

                
                if len(batch_dict) >= batch_size:
                    _bulk_upsert(db, list(batch_dict.values()))
                    processed_count += len(batch_dict)
                    batch_dict = {} 
                    
                    progress = int((processed_count / total_lines) * 100)
                    self.update_state(state='PROGRESS', meta={'current': processed_count, 'total': total_lines, 'percent': progress})

           
            if batch_dict:
                _bulk_upsert(db, list(batch_dict.values()))
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        _trigger_webhooks(db)
        
        return {"status": "Completed", "total_processed": total_lines}

    except Exception as e:
        return {"status": "Failed", "error": str(e)}
    finally:
        db.close()

def _bulk_upsert(db, data):
    if not data:
        return
    stmt = insert(Product).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['sku'],
        set_={
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
            "is_active": stmt.excluded.is_active
        }
    )
    db.execute(stmt)
    db.commit()

def _trigger_webhooks(db):
    hooks = db.query(Webhook).filter(Webhook.is_active == True).all()
    for hook in hooks:
        try:
            requests.post(hook.url, json={"event": "import_completed"}, timeout=5)
        except:
            pass