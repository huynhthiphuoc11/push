import os
from pymongo import MongoClient
from typing import Optional

# Global connections
_mongo_client: Optional[MongoClient] = None
_database = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        mongo_url = os.getenv("MONGO_URI", "mongodb+srv://phuocht22git:251004@cluster0.tpuc7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        _mongo_client = MongoClient(mongo_url)
    return _mongo_client

def get_database():
    global _database
    if _database is None:
        client = get_mongo_client()
        db_name = os.getenv("MONGO_DB", "matching_db")
        _database = client[db_name]
    return _database

# Add your additional database-related functions or classes here if needed.

def close_connections():
    """
    Closes all global database connections.

    This function is intended to be called in the application's shutdown
    event handler to ensure all connections to the database are closed
    before the application exits.
    """
    global _mongo_client, _database
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _database = None
