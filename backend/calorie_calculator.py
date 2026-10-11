# calorie_calculator.py


# --------------------------------
# Activity multipliers
# --------------------------------
ACTIVITY_FACTORS = {
    "sedentary": 1.20,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extremely_active": 1.90
}


# --------------------------------
# Goal calorie adjustments
# --------------------------------
GOAL_ADJUSTMENTS = {
    "lose": -400,
    "maintain": 0,
    "gain": 250
}


# --------------------------------
# Calculate BMR
# --------------------------------
def calculate_bmr(age, sex, height, weight):

    if sex.lower() == "male":

        bmr = (
            10 * weight
            + 6.25 * height
            - 5 * age
            + 5
        )

    elif sex.lower() == "female":

        bmr = (
            10 * weight
            + 6.25 * height
            - 5 * age
            - 161
        )

    else:
        raise ValueError(
            "Sex must be 'male' or 'female'."
        )

    return bmr


# --------------------------------
# Calculate TDEE
# --------------------------------
def calculate_tdee(bmr, activity_level):

    activity_level = activity_level.lower()

    if activity_level not in ACTIVITY_FACTORS:
        raise ValueError(
            "Invalid activity level."
        )

    factor = ACTIVITY_FACTORS[activity_level]

    return bmr * factor


# --------------------------------
# Calculate daily calorie target
# --------------------------------
def calculate_calorie_target(
    age,
    sex,
    height,
    weight,
    activity_level,
    goal
):

    # BMR
    bmr = calculate_bmr(
        age,
        sex,
        height,
        weight
    )

    # TDEE
    tdee = calculate_tdee(
        bmr,
        activity_level
    )

    # Goal adjustment
    goal = goal.lower()

    if goal not in GOAL_ADJUSTMENTS:
        raise ValueError(
            "Goal must be 'lose', 'maintain', or 'gain'."
        )

    adjustment = GOAL_ADJUSTMENTS[goal]

    calorie_target = tdee + adjustment

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "calorie_target": round(calorie_target)
    }


# --------------------------------
# User input
# --------------------------------
def get_user_details():

    print("\n")
    print("=" * 45)
    print("       PERSONAL CALORIE CALCULATOR")
    print("=" * 45)

    # Age
    while True:
        try:
            age = int(input("Enter age: "))

            if age <= 0:
                print("Age must be greater than 0.")
                continue

            break

        except ValueError:
            print("Please enter a valid age.")

    # Sex
    while True:

        sex = input(
            "Enter sex (male/female): "
        ).lower()

        if sex in ["male", "female"]:
            break

        print("Please enter male or female.")

    # Height
    while True:

        try:
            height = float(
                input("Enter height (cm): ")
            )

            if height <= 0:
                print(
                    "Height must be greater than 0."
                )
                continue

            break

        except ValueError:
            print("Please enter a valid height.")

    # Weight
    while True:

        try:
            weight = float(
                input("Enter weight (kg): ")
            )

            if weight <= 0:
                print(
                    "Weight must be greater than 0."
                )
                continue

            break

        except ValueError:
            print("Please enter a valid weight.")

    # Activity level
    print("\nActivity Levels:")
    print("1. Sedentary")
    print("2. Lightly active")
    print("3. Moderately active")
    print("4. Very active")
    print("5. Extremely active")

    activity_options = {
        "1": "sedentary",
        "2": "lightly_active",
        "3": "moderately_active",
        "4": "very_active",
        "5": "extremely_active"
    }

    while True:

        choice = input(
            "Select activity level (1-5): "
        )

        if choice in activity_options:
            activity_level = activity_options[choice]
            break

        print("Please select a number from 1 to 5.")

    # Goal
    print("\nGoals:")
    print("1. Lose weight")
    print("2. Maintain weight")
    print("3. Gain weight")

    goal_options = {
        "1": "lose",
        "2": "maintain",
        "3": "gain"
    }

    while True:

        choice = input(
            "Select goal (1-3): "
        )

        if choice in goal_options:
            goal = goal_options[choice]
            break

        print("Please select 1, 2 or 3.")

    return (
        age,
        sex,
        height,
        weight,
        activity_level,
        goal
    )


# --------------------------------
# Main program
# --------------------------------
if __name__ == "__main__":

    (
        age,
        sex,
        height,
        weight,
        activity_level,
        goal
    ) = get_user_details()

    result = calculate_calorie_target(
        age,
        sex,
        height,
        weight,
        activity_level,
        goal
    )

    print("\n")
    print("=" * 45)
    print("       PERSONALIZED CALORIE TARGET")
    print("=" * 45)

    print(
        f"BMR            : "
        f"{result['bmr']} kcal/day"
    )

    print(
        f"TDEE           : "
        f"{result['tdee']} kcal/day"
    )

    print(
        f"Daily Target   : "
        f"{result['calorie_target']} kcal/day"
    )

    print("=" * 45)