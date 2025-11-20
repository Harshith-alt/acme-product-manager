Acme Product manager

A high-performance web application designed to import large CSV files into a database without crashing or timing out.
*(Note: The free server sleeps when inactive. Please allow 1-2 minutes for the first request to load.)*

##  Features
*   **Bulk Import:** Upload huge CSV files asynchronously using background workers.
*   **Real-Time Progress:** Watch the import percentage update live on the UI.
*   **Smart Deduplication:** Automatically updates existing products (based on SKU) instead of creating duplicates.
*   **Product Management:** View, search, and delete products via a web dashboard.
*   **Webhooks:** Triggers external notifications when an import finishes.

## Tech Stack
*   **Backend:** Python (FastAPI)
*   **Async Processing:** Celery + Redis
*   **Database:** PostgreSQL (SQLAlchemy ORM)
*   **Frontend:** HTML / JavaScript / Tailwind CSS
*   **Deployment:** Docker & Render

 ## To run locally:
You need **Python** and **Docker Desktop** installed.

### 1. Setup
Run the setup script to create the virtual environment and start the Database/Redis containers.
```powershell
./setup_env.ps1
```
### 2. Run the Server
Starts the FastAPI backend
``` powershell
./run_server.ps1
```
### 3. Run the Worker
Starts the Celery background worker to process files
``` powershell
./run_worker.ps1
```
Open your browser and visit: http://127.0.0.1:8000

### 4. Project Structure
acme_importer/

├── app/

│   ├── main.py        

│   ├── tasks.py         
│   ├── database.py  
│   └── models.py        
├── static/             
├── uploads/           
├── docker-compose.yml  
└── requirements.txt     

### 5.Testing
* Create a CSV file with headers: sku, name, description.
* Upload it via the UI.
* Watch the progress bar complete.
* Check the table below to see your products.




