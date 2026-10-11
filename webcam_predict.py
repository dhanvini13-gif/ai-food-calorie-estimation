import cv2
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

from nutrition import calculate_nutrition


# -----------------------------
# Device
# -----------------------------
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# -----------------------------
# Load trained model
# -----------------------------
checkpoint = torch.load(
    r"C:\Users\nandi\Downloads\archive (7)\food20dataset\food20_efficientnet.pth",
    map_location=device
)

classes = checkpoint["classes"]

model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

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
# Start webcam
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam.")
    exit()

print("Webcam started.")
print("Press SPACE to predict.")
print("Press Q to quit.")


while True:

    ret, frame = cap.read()

    if not ret:
        print("Could not read frame.")
        break

    # Instructions
    cv2.putText(
        frame,
        "SPACE = Predict | Q = Quit",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Food Recognition",
        frame
    )

    key = cv2.waitKey(1) & 0xFF


    # -----------------------------
    # Predict
    # -----------------------------
    if key == 32:

        # Convert BGR → RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(
            rgb_frame
        )

        image = transform(image)

        image = image.unsqueeze(0)

        image = image.to(device)


        # -----------------------------
        # Model prediction
        # -----------------------------
        with torch.no_grad():

            output = model(image)

            probabilities = torch.softmax(
                output,
                dim=1
            )

            confidence, predicted = torch.max(
                probabilities,
                1
            )


        food = classes[predicted.item()]

        confidence_value = (
            confidence.item() * 100
        )


        print("\nPrediction")
        print("----------------------")
        print("Food:", food)
        print(
            f"Confidence: {confidence_value:.2f}%"
        )


        # -----------------------------
        # Ask quantity
        # -----------------------------
        while True:

            try:

                quantity = float(
                    input(
                        "\nEnter number of servings/pieces: "
                    )
                )

                if quantity <= 0:

                    print(
                        "Quantity must be greater than 0."
                    )

                    continue

                break

            except ValueError:

                print(
                    "Please enter a valid number."
                )


        # -----------------------------
        # Calculate nutrition
        # -----------------------------
        nutrition = calculate_nutrition(
            food,
            quantity
        )


        # -----------------------------
        # Display result
        # -----------------------------
        print("\nNutrition Estimate")
        print("----------------------")

        print(
            f"Food             : {food}"
        )

        print(
            f"Quantity         : {quantity:g}"
        )

        print(
            f"Estimated Weight : "
            f"{nutrition['weight']:.0f} g"
        )

        print(
            f"Confidence       : "
            f"{confidence_value:.2f}%"
        )

        print(
            f"Calories         : "
            f"{nutrition['calories']:.1f} kcal"
        )

        print(
            f"Protein          : "
            f"{nutrition['protein']:.1f} g"
        )

        print(
            f"Carbs            : "
            f"{nutrition['carbs']:.1f} g"
        )

        print(
            f"Fat              : "
            f"{nutrition['fat']:.1f} g"
        )

        print("----------------------")


    # -----------------------------
    # Quit
    # -----------------------------
    if key == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()