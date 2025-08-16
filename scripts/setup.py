import os
import sys
import subprocess
import shutil

print("Setting up CV Matching System...")

# Create virtual environment
print("Creating virtual environment...")
if not os.path.isdir("venv"):
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
else:
    print("Virtual environment already exists.")

# Activate virtual environment (inform user)
venv_activate = os.path.join("venv", "Scripts", "activate") if os.name == "nt" else os.path.join("venv", "bin", "activate")
print(f"To activate the virtual environment, run: {venv_activate}")

# Install dependencies
print("Installing dependencies...")
subprocess.run([os.path.join("venv", "Scripts", "python.exe"), "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# Copy environment file
print("Setting up environment...")
if os.path.isfile(".env.example"):
    shutil.copy(".env.example", ".env")
    print("Please edit .env file with your configuration")
else:
    print(".env.example file not found. Please create .env manually.")

# Create models directory
print("Creating models directory...")
os.makedirs("models", exist_ok=True)

# Create sample data
print("Creating sample data...")
subprocess.run([os.path.join("venv", "Scripts", "python.exe"), "scripts/create_sample_data.py"], check=True)

print("Setup completed!")
print("")
print("Next steps:")
print("1. Edit .env file with your MongoDB and Elasticsearch configuration")
print("2. Start MongoDB and Elasticsearch services")
print("3. Run: python scripts/setup_database.py --jobs_csv path/to/jobs_clean.csv --candidates_csv path/to/candidates_parsed.csv")
print("4. Start the API: uvicorn app.main:app --host 0.0.0.0 --port 8000")
