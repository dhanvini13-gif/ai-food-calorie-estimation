
from database import (
    save_meal,
    get_connection,
    get_user
)
from nutrition import calculate_nutrition


# -----------------------------------------
# ADD MEAL
# Calculate nutrition and save exactly once
# -----------------------------------------
def add_meal(food, quantity, account_id):

    nutrition = calculate_nutrition(food, quantity)

    if nutrition is None:
        print(f"Nutrition information not found for: {food}")
        return None

    save_meal(
        food,
        quantity,
        nutrition["weight"],
        nutrition["calories"],
        nutrition["protein"],
        nutrition["carbs"],
        nutrition["fat"],
        account_id
    )

    return nutrition


# -----------------------------------------
# GET TODAY'S MEALS FOR ONE ACCOUNT
# -----------------------------------------

def get_today_meals(account_id):
    conn = get_connection()
    conn.row_factory = __import__("sqlite3").Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM meals
        WHERE account_id = ?
          AND meal_time IS NOT NULL
          AND DATE(meal_time) = DATE('now', 'localtime')
        ORDER BY meal_time DESC
    """, (account_id,))

    rows = cursor.fetchall()
    meals = [dict(row) for row in rows]

    conn.close()
    return meals

# -----------------------------------------
# DAILY CALORIE TARGET
# -----------------------------------------
def get_daily_calorie_target(account_id):

    user = get_user(account_id)

    if user is None:
        return 2000.0

    target = user.get("daily_calorie_target")

    if target is None:
        return 2000.0

    return float(target)


# -----------------------------------------
# DAILY SUMMARY FOR ONE ACCOUNT
# -----------------------------------------
def get_daily_summary(account_id):

    meals = get_today_meals(account_id)
    target = get_daily_calorie_target(account_id)

    calories = sum(float(m.get("calories") or 0) for m in meals)
    protein = sum(float(m.get("protein") or 0) for m in meals)
    carbs = sum(float(m.get("carbs") or 0) for m in meals)
    fat = sum(float(m.get("fat") or 0) for m in meals)

    return {
        "calories": round(calories, 2),
        "protein": round(protein, 2),
        "carbs": round(carbs, 2),
        "fat": round(fat, 2),
        "remaining": round(target - calories, 2),
        "percentage": round(calories / target * 100, 2) if target > 0 else 0,
        "target": target,
        "meals": meals
    }


# -----------------------------------------
# DISPLAY SUMMARY (STANDALONE SCRIPT)
# -----------------------------------------
def display_summary(account_id):

    summary = get_daily_summary(account_id)

    print("\n" + "=" * 55)
    print("          FOOD20 DAILY NUTRITION SUMMARY")
    print("=" * 55)
    print(f"Calories       : {summary['calories']:.1f} kcal")
    print(f"Protein        : {summary['protein']:.1f} g")
    print(f"Carbohydrates  : {summary['carbs']:.1f} g")
    print(f"Fat            : {summary['fat']:.1f} g")
    print(f"Calories Left  : {summary['remaining']:.1f} kcal")
    print(f"Daily Target   : {summary['target']:.0f} kcal")
    print(f"Target Used    : {summary['percentage']:.1f}%")

    print("\nMEAL-WISE BREAKDOWN")
    print("-" * 55)

    for index, meal in enumerate(summary["meals"], start=1):
        print(
            f"{index}. {meal.get('meal_time')} | "
            f"{meal.get('food')} | "
            f"{meal.get('quantity')} serving(s) | "
            f"{float(meal.get('calories') or 0):.1f} kcal | "
            f"Fat: {float(meal.get('fat') or 0):.1f} g"
        )

    print("=" * 55)
