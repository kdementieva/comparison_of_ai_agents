import sqlite3


DB_NAME = "comparison.db"


def create_table():
  connection = sqlite3.connect(DB_NAME)
  cursor = connection.cursor()

  cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      model_name TEXT,
      question TEXT,
      answer TEXT,
      temperature REAL,
      context_depth INTEGER,
      prompt_accuracy TEXT,
      matches_document INTEGER
    )
  """)

  connection.commit()
  connection.close()


def save_experiment(
    model_name,
    question,
    answer,
    temperature,
    context_depth,
    prompt_accuracy,
    matches_document
):
  connection = sqlite3.connect(DB_NAME)
  cursor = connection.cursor()

  cursor.execute("""
    INSERT INTO experiments (
      model_name,
      question,
      answer,
      temperature,
      context_depth,
      prompt_accuracy,
      matches_document
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
  """, (
    model_name,
    question,
    answer,
    temperature,
    context_depth,
    prompt_accuracy,
    matches_document
  ))

  connection.commit()
  connection.close()


create_table()
