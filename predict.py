from PIL import Image
import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from daily_tracker import add_meal, display_summary

# 1. Set device FIRST
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# 2. Locate the backend model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

MODEL_PATH = os.path.join(
    BACKEND_DIR,
    "food20_efficientnet.pth"
)

if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

# 3. Load checkpoint
checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

classes = checkpoint["classes"]

# 4. Create and load model
model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)

model.load_state_dict(checkpoint["model_state_dict"])
model = model.to(device)
model.eval()


# -----------------------------
# Image preprocessing
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -----------------------------
# Load image
# -----------------------------
IMAGE_PATH = os.path.join(
    BASE_DIR,
    "my_images",
    "food1.jpg"
)

if not os.path.isfile(IMAGE_PATH):
    raise FileNotFoundError(
        f"Image not found: {IMAGE_PATH}\n"
        "Place a test image at backend/my_images/food1.jpg "
        "or update IMAGE_PATH in predict.py."
    )

image = Image.open(IMAGE_PATH).convert("RGB")

image_tensor = transform(image).unsqueeze(0).to(device)


# -----------------------------
# Predict food
# -----------------------------
with torch.no_grad():
    output = model(image_tensor)
    probabilities = torch.softmax(output, dim=1)
    confidence, predicted = torch.max(probabilities, dim=1)

predicted_class = classes[predicted.item()]
confidence_value = confidence.item() * 100


# -----------------------------
# Display prediction
# -----------------------------
print("\nFood Prediction")
print("----------------------")
print(f"Food       : {predicted_class}")
print(f"Confidence : {confidence_value:.2f}%")


# -----------------------------
# Ask for quantity
# -----------------------------
while True:
    try:
        quantity = float(
            input("\nEnter number of servings/pieces: ")
        )

        if quantity <= 0:
            print("Quantity must be greater than 0.")
            continue

        break

    except ValueError:
        print("Please enter a valid number.")


# -----------------------------
# Calculate nutrition and save once
# -----------------------------
nutrition = add_meal(predicted_class, quantity)

if nutrition is None:
    raise ValueError(
        f"Nutrition information not found for '{predicted_class}'."
    )


# -----------------------------
# Display nutrition
# -----------------------------
print("\nNutrition Estimate")
print("----------------------")
print(f"Food             : {predicted_class}")
print(f"Quantity         : {quantity:g}")
print(f"Estimated Weight : {nutrition['weight']:.1f} g")
print(f"Confidence       : {confidence_value:.2f}%")
print(f"Calories         : {nutrition['calories']:.1f} kcal")
print(f"Protein          : {nutrition['protein']:.1f} g")
print(f"Carbs            : {nutrition['carbs']:.1f} g")
print(f"Fat              : {nutrition['fat']:.1f} g")
print("----------------------")


# -----------------------------
# Display daily summary
# -----------------------------
display_summary()
