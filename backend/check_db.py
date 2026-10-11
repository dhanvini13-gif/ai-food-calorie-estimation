import sqlite3

connection = sqlite3.connect("food_calorie.db")

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables:", tables)

connection.close()