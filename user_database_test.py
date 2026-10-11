from calorie_calculator import calculate_calorie_target
from user_database import save_user, get_user


# User details
age = 20
sex = "female"
height = 157
weight = 39
activity_level = "lightly_active"
goal = "gain"


# Calculate calories
result = calculate_calorie_target(
    age,
    sex,
    height,
    weight,
    activity_level,
    goal
)


# Save user
user_id = save_user(
    age,
    sex,
    height,
    weight,
    activity_level,
    goal,
    result["bmr"],
    result["tdee"],
    result["calorie_target"]
)


print("\nUser ID:", user_id)


# Retrieve user
user = get_user(user_id)


print("\nSaved User")
print("----------------------")
print("Age:", user["age"])
print("Sex:", user["sex"])
print("Height:", user["height"])
print("Weight:", user["weight"])
print("Activity:", user["activity_level"])
print("Goal:", user["goal"])
print("BMR:", user["bmr"])
print("TDEE:", user["tdee"])
print(
    "Daily Target:",
    user["daily_calorie_target"]
)