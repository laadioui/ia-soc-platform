$env:PYTHONPATH = "C:\Users\msi\Downloads\ia soc plateform\services\collector-service"
Set-Location "C:\Users\msi\Downloads\ia soc plateform\services\collector-service"
& "C:\Users\msi\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
