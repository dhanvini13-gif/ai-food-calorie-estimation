from nutrition import calculate_nutrition

food = "dosa"
weight = 120

result = calculate_nutrition(food, weight)

print("Food:", food)
print("Weight:", weight, "g")
print("Calories:", round(result["calories"], 2), "kcal")
print("Protein:", round(result["protein"], 2), "g")
print("Carbs:", round(result["carbs"], 2), "g")
print("Fat:", round(result["fat"], 2), "g")