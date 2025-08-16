import os
import sys
import subprocess
import shutil
import requests

print("Starting CV Matching System...")

# Check if virtual environment exists
if not os.path.isdir("venv"):
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
else:
    print("Virtual environment already exists.")

# Activate virtual environment (inform user)
venv_activate = os.path.join("venv", "Scripts", "activate") if os.name == "nt" else os.path.join("venv", "bin", "activate")
print(f"To activate the virtual environment, run: {venv_activate}")

# Install/update dependencies
print("Installing dependencies...")
subprocess.run([os.path.join("venv", "Scripts", "python.exe"), "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# Check if .env exists
if not os.path.isfile(".env"):
    print("Creating .env from template...")
    if os.path.isfile(".env.example"):
        shutil.copy(".env.example", ".env")
        print("Please edit .env file with your configuration")
    else:
        print(".env.example file not found. Please create .env manually.")

# Check MongoDB (inform user)
print("Checking MongoDB...")
# Windows: check service status
if os.name == "nt":
    from subprocess import PIPE
    result = subprocess.run(["sc", "query", "MongoDB"], stdout=PIPE, stderr=PIPE, text=True)
    if "RUNNING" not in result.stdout:
        print("Please start MongoDB service")
        print("Windows: net start MongoDB")
else:
    print("Please ensure MongoDB is running on your system.")

# Check Elasticsearch
print("Checking Elasticsearch...")
try:
    response = requests.get("http://localhost:9200", timeout=2)
    if response.status_code != 200:
        raise Exception()
except Exception:
    print("Please start Elasticsearch service")
    print("Make sure Elasticsearch is running on http://localhost:9200")

# Setup database if needed
if len(sys.argv) > 1 and sys.argv[1] == "--setup":
    print("Setting up database...")
    if len(sys.argv) < 4:
        print(f"Usage: python {os.path.basename(__file__)} --setup <jobs_csv_path> <candidates_csv_path>")
        sys.exit(1)
    jobs_csv = sys.argv[2]
    candidates_csv = sys.argv[3]
    subprocess.run([
        os.path.join("venv", "Scripts", "python.exe"),
        "scripts/setup_database.py",
        "--jobs_csv", jobs_csv,
        "--candidates_csv", candidates_csv
    ], check=True)

# Start the API server
print("Starting FastAPI server...")
subprocess.run([
    os.path.join("venv", "Scripts", "python.exe"),
    "-m", "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
], check=True)
