# database.py
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_database():
    conn = sqlite3.connect("reconciliation.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS recon_history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      riskdate TEXT,
                      quantity_a REAL,
                      quantity_b REAL,
                      tolerance REAL,
                      comment TEXT,
                      embedding BLOB)''')
    conn.commit()
    conn.close()

def insert_historical_data(df):
    conn = sqlite3.connect("reconciliation.db")
    cursor = conn.cursor()
    for _, row in df.iterrows():
        # Adjust column names if needed.
        text = f"{row['riskdate']} {row['quantity_a']} {row['quantity_b']} {row['tolerance']} {row['comment']}"
        embedding = model.encode(text).tobytes()
        cursor.execute("INSERT INTO recon_history (riskdate, quantity_a, quantity_b, tolerance, comment, embedding) VALUES (?, ?, ?, ?, ?, ?)",
                       (row['riskdate'], row['quantity_a'], row['quantity_b'], row['tolerance'], row['comment'], embedding))
    conn.commit()
    conn.close()

def fetch_data():
    """Fetch all records from the recon_history table."""
    conn = sqlite3.connect("reconciliation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recon_history")
    rows = cursor.fetchall()
    conn.close()
    return rows

def retrieve_similar_cases(query_text, top_n=3):
    query_embedding = model.encode(query_text)
    conn = sqlite3.connect("reconciliation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT riskdate, quantity_a, quantity_b, tolerance, comment, embedding FROM recon_history")
    
    results = []
    for row in cursor.fetchall():
        db_text = f"{row[0]} {row[1]} {row[2]} {row[3]} {row[4]}"
        db_embedding = np.frombuffer(row[5], dtype=np.float32)
        similarity = np.dot(query_embedding, db_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(db_embedding))
        results.append((db_text, similarity))
    
    results.sort(key=lambda x: x[1], reverse=True)
    conn.close()
    return [res[0] for res in results[:top_n]]

def seed_dummy_data():
    import pandas as pd
    # Create a DataFrame with more dummy records
    data = {
        "riskdate": [
            "2025-03-25", "2025-03-25", "2025-03-24", "2025-03-23", 
            "2025-03-22", "2025-03-21", "2025-03-20", "2025-03-19"
        ],
        "quantity_a": [100, 250, 300, 150, 400, 200, 350, 500],
        "quantity_b": [90, 250, 310, 140, 395, 205, 360, 480],
        "tolerance": [5, 5, 10, 5, 8, 5, 10, 15],
        "comment": [
            "Slight discrepancy", 
            "No issue", 
            "Minor overage", 
            "Under-reporting detected", 
            "Close match", 
            "Minor adjustment", 
            "Slight overage", 
            "Potential reporting error"
        ]
    }
    df = pd.DataFrame(data)
    # Insert dummy data into the database
    from database import insert_historical_data
    insert_historical_data(df)
    print("✅ Seeded dummy data into the database.")


if __name__=="__main__":
    #create_database()
    seed_dummy_data()
