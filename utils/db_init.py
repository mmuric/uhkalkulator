#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import csv
import os

def init_database():
    db_path = "data/items.db"
    csv_path = "data/items.csv"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gram REAL NOT NULL,
        unit TEXT NOT NULL,
        carbs_g REAL NOT NULL,
        protein_g REAL,
        fat_g REAL,
        category TEXT DEFAULT 'food'
    )
    """)
    
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
            INSERT INTO items (name, gram, unit, carbs_g, protein_g, fat_g, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row['name'],
                float(row['gram']),
                row['unit'],
                float(row['carbs_g']),
                float(row.get('protein_g', 0)),
                float(row.get('fat_g', 0)),
                row.get('category', 'food')
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Baza kreirana: {db_path}")

if __name__ == "__main__":
    init_database()
