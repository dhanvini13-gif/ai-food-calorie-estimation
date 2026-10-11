import io

import torch
import torch.nn as nn

from torchvision import transforms, models
from PIL import Image

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from database import (
    initialize_database,
    create_account,
    authenticate_user
)

from nutrition import calculate_nutrition
from daily_tracker import add_meal, get_daily_summary


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Food Calorie Estimation API",
    description="AI-powered Indian food calorie estimation system",
    version="1.0"
)
class AccountRequest(BaseModel):
    username: str
    password: str


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-food-calorie-estimation.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# --------------------------------------------------
# LOAD AI MODEL
# --------------------------------------------------

MODEL_PATH = "food20_efficientnet.pth"

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

classes = checkpoint["classes"]

model = models.efficientnet_b0(
    weights=None
)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


# --------------------------------------------------
# IMAGE TRANSFORMATION
# --------------------------------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# REQUEST MODEL FOR LOGIN / SIGNUP
# --------------------------------------------------

class AccountRequest(BaseModel):
    username: str
    password: str


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Food Calorie Estimation API is running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@app.post("/signup")
def signup(data: AccountRequest):

    username = data.username.strip()
    password = data.password

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required."
        )

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must be at least 3 characters."
        )

    if len(password) < 4:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 4 characters."
        )

    account = create_account(
        username,
        password
    )

    if account is None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    return {
        "message": "Account created successfully.",
        "account_id": account["account_id"],
        "username": account["username"]
    }
# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.post("/login")
def login(data: AccountRequest):

    username = data.username.strip()
    password = data.password

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required."
        )

    user = authenticate_user(
        username,
        password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    return {
        "message": "Login successful.",
        "account_id": user["account_id"],
        "username": user["username"]
    }


# --------------------------------------------------
# FOOD PREDICTION
# --------------------------------------------------


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    quantity: float = Form(...),
     account_id: int = Form(...),
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0."
        )

    # Read uploaded image
    image_bytes = await file.read()

    try:
        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )

    # Transform image
    image_tensor = transform(image).unsqueeze(0).to(device)

    # AI prediction
    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    predicted_class = classes[predicted.item()]
    confidence_value = confidence.item() * 100

    # Calculate nutrition and save the meal ONCE
    food = predicted_class.lower().strip()
    nutrition = add_meal(food, quantity, account_id)

    if nutrition is None:
        raise HTTPException(
            status_code=400,
            detail=f"Nutrition information not found for {food}"
        )

    # Return result — do not call add_meal again
    return {
        "food": food,
        "confidence": round(confidence_value, 2),
        "quantity": quantity,
        "weight": nutrition["weight"],
        "calories": nutrition["calories"],
        "protein": nutrition["protein"],
        "carbs": nutrition["carbs"],
        "fat": nutrition["fat"]
    }



# --------------------------------------------------
# DAILY SUMMARY
# --------------------------------------------------

@app.get("/daily-summary")
def daily_summary(account_id: int):
    return get_daily_summary(account_id)