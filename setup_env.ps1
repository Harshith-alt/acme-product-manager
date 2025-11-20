python -m venv venv

.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt

docker-compose up -d

Write-Host "Setup Complete. Containers are running. Venv created."