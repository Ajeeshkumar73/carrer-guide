from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review

def index(request):
    reviews = Review.objects.all().order_by("-created_at")  # last 5 reviews
    return render(request, "home.html", {"reviews": reviews})

def user_page(request):
    return render(request, "user_page.html")

def predict_page(request):
    return render(request, "predict_page.html")

def assistant(request):
    return render(request, "assistant.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("home")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("home")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect("home")

    return redirect("home")

# Login
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect("userpage")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("home")

    return redirect("home")

# Logout
def logout_view(request):
    logout(request)
    return redirect("home")

# Dashboard
@login_required(login_url='login')
def userpage_view(request):
    return render(request, "userpage.html")

# Review submission
@login_required(login_url="login")
def submit_review(request):
    if request.method == "POST":
        text = request.POST.get("review")
        rating = request.POST.get("rating")

        if text and rating:
            Review.objects.create(user=request.user, text=text, rating=rating)
            messages.success(request, "Review posted successfully!")

    return redirect("userpage")


