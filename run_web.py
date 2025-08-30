import subprocess
import sys
import webbrowser
import time

try:
    import uvicorn
except ImportError:
    print("[ERRO] Uvicorn não está instalado. Rode: pip install -r requirements.txt")
    sys.exit(1)

try:
    import fastapi
except ImportError:
    print("[ERRO] FastAPI não está instalado. Rode: pip install -r requirements.txt")
    sys.exit(1)

# Inicia o servidor Uvicorn em background
proc = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "web.app:app", "--reload"
])

# Aguarda o servidor subir
print("Aguardando o servidor iniciar...")
time.sleep(2)

# Abre o navegador na interface
webbrowser.open("http://127.0.0.1:8000")

try:
    proc.wait()
except KeyboardInterrupt:
    print("Encerrando servidor...")
    proc.terminate()
