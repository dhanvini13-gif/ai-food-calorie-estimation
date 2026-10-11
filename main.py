
import os
import io

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    initialize_database,
    create_account,
    authenticate_user,
)
from daily_tracker import (
    add_meal,
    get_daily_summary,
)


# =========================================
# DATABASE INITIALIZATION
# =========================================

initialize_database()

app = FastAPI(title="Food Calorie Estimation API")


# =========================================
# CORS CONFIGURATION
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# MODEL CONFIGURATION
# =========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR,
    "food20_efficientnet.pth",
)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# IMPORTANT:
# Keep this list in exactly the same order as
# the classes used when training your model.
classes = [
    "burger",
    "butter_naan",
    "chai",
    "chapati",
    "chole_bhature",
    "dal_makhani",
    "dhokla",
    "fried_rice",
    "idli",
    "jalebi",
    "kaathi_rolls",
    "kadai_paneer",
    "kulfi",
    "masala_dosa",
    "momos",
    "paani_puri",
    "pakode",
    "pav_bhaji",
    "pizza",
    "samosa",
]


# =========================================
# LOAD EFFICIENTNET-B0 MODEL
# =========================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes),
)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device,
    )
)

model.to(device)
model.eval()


# =========================================
# IMAGE TRANSFORMATION
# =========================================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


# =========================================
# ACCOUNT REQUEST MODEL
# =========================================

class AccountRequest(BaseModel):
    username: str
    password: str


# =========================================
# HOME ENDPOINT
# =========================================

@app.get("/")
def home():
    return {
        "message": "Food Calorie Estimation API is running"
    }


# =========================================
# SIGNUP
# =========================================

@app.post("/signup")
def signup(request: AccountRequest):
    username = request.username.strip()

    if not username or not request.password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required.",
        )

    try:
        account = create_account(
            username,
            request.password,
        )

        return {
            "message": "Account created successfully",
            "account_id": account["account_id"],
            "username": account["username"],
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=(
                "Account creation failed. "
                "The username may already exist."
            ),
        ) from error


# =========================================
# LOGIN
# =========================================

@app.post("/login")
def login(request: AccountRequest):
    account = authenticate_user(
        request.username.strip(),
        request.password,
    )

    if not account:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    return {
        "message": "Login successful",
        "account_id": account["account_id"],
        "username": account["username"],
    }


# =========================================
# FOOD PREDICTION
# =========================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    quantity: float = Form(...),
    account_id: int = Form(...),
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero.",
        )

    if account_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid account ID.",
        )

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image.",
        )

    try:
        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

        image_tensor = transform(
            image
        ).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image_tensor)

            probabilities = torch.softmax(
                outputs,
                dim=1,
            )

            confidence, predicted_index = torch.max(
                probabilities,
                dim=1,
            )

        predicted_class = classes[
            predicted_index.item()
        ]

        confidence_value = round(
            confidence.item() * 100,
            2,
        )

        food = predicted_class.lower().strip()

        # Save the meal once and store the returned nutrition
        nutrition = add_meal(food, quantity, account_id)

        if nutrition is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nutrition information not found for {food}.",
            )

        return {
            "food": food,
            "confidence": confidence_value,
            "quantity": quantity,
            "estimated_weight": nutrition["weight"],
            "calories": nutrition["calories"],
            "protein": nutrition["protein"],
            "carbs": nutrition["carbs"],
            "fat": nutrition["fat"],
            "account_id": account_id,
        }   

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}",
        ) from error


# =========================================
# DAILY NUTRITION SUMMARY
# =========================================

@app.get("/daily-summary")
def daily_summary(account_id: int):
    if account_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid account ID.",
        )

    return get_daily_summary(account_id)
