import sys
import os
import subprocess

print("Setting up CV Matching System with your data...")

if len(sys.argv) != 3:
    print(f"Usage: python {os.path.basename(__file__)} <jobs_csv_path> <candidates_csv_path>")
    print("Example: python run_setup.py /path/to/jobs_clean.csv /path/to/candidates_parsed.csv")
    sys.exit(1)

jobs_csv = sys.argv[1]
candidates_csv = sys.argv[2]

if not os.path.isfile(jobs_csv):
    print(f"Error: Jobs CSV file not found: {jobs_csv}")
    sys.exit(1)

if not os.path.isfile(candidates_csv):
    print(f"Error: Candidates CSV file not found: {candidates_csv}")
    sys.exit(1)

print("Setting up database with:")
print(f"Jobs CSV: {jobs_csv}")
print(f"Candidates CSV: {candidates_csv}")

subprocess.run([
    sys.executable,
    "scripts/setup_database.py",
    "--jobs_csv", jobs_csv,
    "--candidates_csv", candidates_csv
], check=True)

print("Database setup completed!")
print("You can now start the system with: python scripts/start_system.py")
