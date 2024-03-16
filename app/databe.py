# database.py

import sqlite3
import os

def initialize_database(app):
    DATABASE_PATH = os.path.join(app.root_path, 'static', 'misc', 'feedback.db')
    
    # Ensure the directory for the database exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    # Create the database and table if they don't exist
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emoji TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
