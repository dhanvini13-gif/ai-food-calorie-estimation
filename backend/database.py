import sqlite3
import hashlib
import os


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_NAME = os.path.join(
    BASE_DIR,
    "food_calorie.db"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ==================================================
# INITIALIZE DATABASE
# ==================================================


def initialize_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                age INTEGER,
                sex TEXT,
                height REAL,
                weight REAL,
                activity_level TEXT,
                goal TEXT,
                bmr REAL,
                tdee REAL,
                daily_calorie_target REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                food TEXT,
                quantity TEXT,
                estimated_weight REAL,
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                meal_time TEXT DEFAULT CURRENT_TIMESTAMP,
                account_id INTEGER
            )
        """)

        # Migrate existing databases safely.
        cursor.execute("PRAGMA table_info(meals)")
        columns = [row[1] for row in cursor.fetchall()]

        if "meal_time" not in columns:
            cursor.execute(
                "ALTER TABLE meals ADD COLUMN meal_time TEXT"
            )

        if "account_id" not in columns:
            cursor.execute(
                "ALTER TABLE meals ADD COLUMN account_id INTEGER"
            )

        connection.commit()
        print("SQLite database initialized successfully.")
        print("Database path:", DATABASE_NAME)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_meal(
    food,
    quantity,
    weight,
    calories,
    protein,
    carbs,
    fat,
    account_id
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO meals (
                food, quantity, estimated_weight,
                calories, protein, carbs, fat,
                meal_time, account_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """, (
            str(food),
            str(quantity),
            float(weight),
            float(calories),
            float(protein),
            float(carbs),
            float(fat),
            int(account_id)
        ))

        connection.commit()
        meal_id = cursor.lastrowid

        print(
            f"Meal saved: ID={meal_id}, "
            f"account={account_id}, food={food}"
        )

        return meal_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()



# ==================================================
# PASSWORD HASH
# ==================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ==================================================
# CREATE ACCOUNT
# ==================================================

def create_account(username, password):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        hashed_password = hash_password(password)

        cursor.execute(
            """
            INSERT INTO accounts (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                username,
                hashed_password
            )
        )

        connection.commit()

        account_id = cursor.lastrowid

        return {
            "account_id": account_id,
            "username": username
        }

    except sqlite3.IntegrityError:

        return None

    finally:
        connection.close()


# ==================================================
# AUTHENTICATE USER
# ==================================================

def authenticate_user(username, password):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        hashed_password = hash_password(password)

        cursor.execute(
            """
            SELECT
                rowid AS account_id,
                username
            FROM accounts
            WHERE username = ?
              AND password = ?
            """,
            (
                username,
                hashed_password
            )
        )

        row = cursor.fetchone()

        if row:

            return {
                "account_id": row[0],
                "username": row[1]
            }

        return None

    finally:
        connection.close()


# ==================================================
# SAVE USER PROFILE
# ==================================================

def save_user(
    age,
    sex,
    height,
    weight,
    activity_level,
    goal,
    bmr,
    tdee,
    calorie_target
):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO users (
                age,
                sex,
                height,
                weight,
                activity_level,
                goal,
                bmr,
                tdee,
                daily_calorie_target
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            age,
            sex,
            height,
            weight,
            activity_level,
            goal,
            bmr,
            tdee,
            calorie_target
        )

        cursor.execute(query, values)

        connection.commit()

        user_id = cursor.lastrowid

        print("User profile saved successfully.")

        return user_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==================================================
# GET USER PROFILE
# ==================================================

def get_user(user_id):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            description[0]
            for description in cursor.description
        ]

        return dict(
            zip(columns, row)
        )

    finally:
        connection.close()


# ==================================================
# INITIALIZE WHEN RUN DIRECTLY
# ==================================================

if __name__ == "__main__":
    initialize_database()