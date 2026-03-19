from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import random

# TEMP OTP STORAGE (use DB later)
otp_storage = {}

# ================= LOGIN =================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return JsonResponse({"status": "success", "redirect": "/"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials"})

# ================= SIGNUP =================
def signup_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"status": "error", "message": "Username already exists"})

        if User.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already exists"})

        # generate OTP
        otp = str(random.randint(100000, 999999))

        otp_storage[email] = {
            "username": username,
            "password": password,
            "otp": otp
        }

        print("OTP:", otp)  # 👉 see in terminal

        return JsonResponse({"status": "otp_sent"})

# ================= VERIFY OTP =================
def verify_otp(request):
    if request.method == "POST":

        email = request.POST.get("email")
        otp = request.POST.get("otp")

        data = otp_storage.get(email)

        if not data:
            return JsonResponse({"status": "error", "message": "OTP expired"})

        if data["otp"] != otp:
            return JsonResponse({"status": "error", "message": "Invalid OTP"})

        # create user
        user = User.objects.create_user(
            username=data["username"],
            email=email,
            password=data["password"]
        )

        # auto-login after signup
        user = authenticate(request, username=data["username"], password=data["password"])
        if user:
            login(request, user)

        del otp_storage[email]

        return JsonResponse({"status": "success", "redirect": "/"})

# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("/")