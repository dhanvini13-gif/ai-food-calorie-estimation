# Approximate nutrition values per 100 g
NUTRITION_DB = {
    "biriyani": {
        "calories": 180,
        "protein": 6.0,
        "carbs": 25.0,
        "fat": 6.0
    },

    "bisibelebath": {
        "calories": 150,
        "protein": 4.0,
        "carbs": 25.0,
        "fat": 4.0
    },

    "butternaan": {
        "calories": 310,
        "protein": 8.0,
        "carbs": 48.0,
        "fat": 9.0
    },

    "chaat": {
        "calories": 180,
        "protein": 5.0,
        "carbs": 28.0,
        "fat": 6.0
    },

    "chappati": {
        "calories": 250,
        "protein": 8.0,
        "carbs": 45.0,
        "fat": 4.0
    },

    "dhokla": {
        "calories": 160,
        "protein": 6.0,
        "carbs": 25.0,
        "fat": 4.0
    },

    "dosa": {
        "calories": 168,
        "protein": 4.5,
        "carbs": 30.0,
        "fat": 3.5
    },

    "gulab jamun": {
        "calories": 330,
        "protein": 4.0,
        "carbs": 55.0,
        "fat": 10.0
    },

    "halwa": {
        "calories": 300,
        "protein": 4.0,
        "carbs": 45.0,
        "fat": 12.0
    },

    "idly": {
        "calories": 130,
        "protein": 4.0,
        "carbs": 26.0,
        "fat": 1.0
    },

    "kathi roll": {
        "calories": 250,
        "protein": 9.0,
        "carbs": 30.0,
        "fat": 10.0
    },

    "meduvadai": {
        "calories": 280,
        "protein": 8.0,
        "carbs": 30.0,
        "fat": 14.0
    },

    "noodles": {
        "calories": 190,
        "protein": 5.0,
        "carbs": 30.0,
        "fat": 6.0
    },

    "paniyaram": {
        "calories": 180,
        "protein": 4.0,
        "carbs": 28.0,
        "fat": 6.0
    },

    "poori": {
        "calories": 330,
        "protein": 6.0,
        "carbs": 45.0,
        "fat": 14.0
    },

    "samosa": {
        "calories": 300,
        "protein": 6.0,
        "carbs": 35.0,
        "fat": 15.0
    },

    "tandoori chicken": {
        "calories": 220,
        "protein": 27.0,
        "carbs": 5.0,
        "fat": 10.0
    },

    "upma": {
        "calories": 150,
        "protein": 4.0,
        "carbs": 25.0,
        "fat": 4.0
    },

    "vada pav": {
        "calories": 290,
        "protein": 7.0,
        "carbs": 40.0,
        "fat": 12.0
    },

    "ven pongal": {
        "calories": 180,
        "protein": 5.0,
        "carbs": 27.0,
        "fat": 6.0
    }
}


# Estimated weight of ONE serving/piece in grams
SERVING_SIZE = {
    "biriyani": 250,
    "bisibelebath": 250,
    "butternaan": 100,
    "chaat": 200,
    "chappati": 40,
    "dhokla": 50,
    "dosa": 100,
    "gulab jamun": 50,
    "halwa": 100,
    "idly": 50,
    "kathi roll": 200,
    "meduvadai": 60,
    "noodles": 250,
    "paniyaram": 30,
    "poori": 40,
    "samosa": 80,
    "tandoori chicken": 150,
    "upma": 200,
    "vada pav": 120,
    "ven pongal": 250
}


def calculate_nutrition(food, quantity):
    """
    Calculate nutrition based on number of servings/pieces.
    """

    if food not in NUTRITION_DB:
        return None

    nutrition = NUTRITION_DB[food]

    weight_per_serving = SERVING_SIZE[food]

    total_weight = weight_per_serving * quantity

    multiplier = total_weight / 100

    return {
        "weight": total_weight,
        "calories": nutrition["calories"] * multiplier,
        "protein": nutrition["protein"] * multiplier,
        "carbs": nutrition["carbs"] * multiplier,
        "fat": nutrition["fat"] * multiplier
    }