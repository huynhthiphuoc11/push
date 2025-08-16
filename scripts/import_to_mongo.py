import pandas as pd
from pymongo import MongoClient
import os

def import_csv_to_mongo(csv_path, collection_name, mongo_uri, mongo_db):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    col = db[collection_name]
    col.insert_many(records)
    print(f"Imported {len(records)} records from {csv_path} to collection '{collection_name}'")

if __name__ == "__main__":
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "matching_db")
    # Import candidates
    import_csv_to_mongo(r"data/candidates_parsed.csv", "candidates", mongo_uri, mongo_db)
    import_csv_to_mongo(r"data/UpdatedResumeDataSet.csv", "candidates", mongo_uri, mongo_db)
    # Import jobs
    import_csv_to_mongo(r"data/final_job.csv", "jobs", mongo_uri, mongo_db)
