import sqlite3
from pathlib import Path

DB_PATH = Path("db/nifty100.db")
SCHEMA = Path("db/schema.sql")


def create_database():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()

    conn.close()

    print("Database Created Successfully")


if __name__ == "__main__":

    create_database()