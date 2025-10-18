from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review
import joblib
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

# Get the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the trained model
MODEL_PATH = os.path.join(BASE_DIR, "career_rf_model.pkl")

# Load the trained model
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"Error: Model file not found at {MODEL_PATH}")

@csrf_exempt
def predict_career(request):
    if request.method == "POST":
        if model is None:
            return JsonResponse({"error": "Model not loaded"}, status=500)

        try:
            data = json.loads(request.body)
            # Convert input data to DataFrame
            df = pd.DataFrame([data])

            # Make prediction
            pred = model.predict(df)[0]  # predicted career domain

            return JsonResponse({"career_domain": pred})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request, use POST"}, status=400)


def index(request):  # last 5 reviews
    return render(request, "home.html")



def predict_page(request):
    return render(request, "predict_page.html")

def assistant(request):
    return render(request, "assistant.html")

def log(request):
    return render(request, "login_reg.html")

def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("login")  # make sure this URL renders login template

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("login")

        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")  # redirect to login page so user can see message

    # If GET request, show registration/login page
    return render(request, "login_reg.html") 

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user_auth = None

        if user_auth:
            login(request, user_auth)
            return redirect("login_assistant")  # make sure this URL exists in urls.py
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("login")  # render template with messages

    # If GET request, show login page
    return render(request, "login_reg.html")  # template must contain messages block


# Logout
def logout_view(request):
    logout(request)
    return redirect("home")

# User Dashboard
@login_required(login_url="login_reg")
def login_assistant(request):
    return render(request, "login_assistant.html", {"email": request.user.email})

