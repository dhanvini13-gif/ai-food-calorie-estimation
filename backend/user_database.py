from database import get_connection


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
    cursor = connection.cursor()

    query = """
        INSERT INTO users
        (
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

    cursor.close()
    connection.close()

    print("User profile saved successfully.")

    return user_id


def get_user(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        SELECT *
        FROM users
        WHERE user_id = ?
    """

    cursor.execute(query, (user_id,))

    row = cursor.fetchone()

    if row:
        columns = [description[0] for description in cursor.description]
        user = dict(zip(columns, row))
    else:
        user = None

    cursor.close()
    connection.close()

    return user