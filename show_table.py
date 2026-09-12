import sqlite3
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 120)

with sqlite3.connect("comparison.db") as connection:
    df = pd.read_sql_query("SELECT * FROM experiments", connection)

print(df)