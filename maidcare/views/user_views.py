from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import hashlib 
from bson import ObjectId


# ================== HELPER ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================== USER REGISTER ==================
def user_register(request):
    users_collection = settings.DB["users"]

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone=request.POST.get("phone")

        # check existing user
        existing = users_collection.find_one({"email": email})

        if existing:
            messages.error(request, "User already exists")
            return redirect("user_register")

        if len(password) < 4:
            messages.error(request, "Password must be at least 6 characters")
            return redirect("user_register")

        users_collection.insert_one({
            "name": name,
            "email": email,
            "phone":phone,
            "password": hash_password(password),
            "role": "user"
        })

        messages.success(request, "Registration successful")
        return redirect("user_login")

    return render(request, "user_register.html")


# ================== USER LOGIN ==================
def user_login(request):
    users_collection = settings.DB["users"]

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = users_collection.find_one({
            "email": email,
            "password": hash_password(password)
        })

        if user:
            request.session["user_logged_in"] = True
            request.session["user_email"] = email
            request.session["user_name"] = user["name"]
            request.session["role"] = "user"

            return redirect("home")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "user_login.html")

def user_forgot_password(request):
    users_collection = settings.DB["users"]

    if request.method == "POST":
        email = request.POST.get("email")

        user = users_collection.find_one({"email": email})

        if not user:
            messages.error(request, "Email not found")
            return redirect("/user-forgot-password/")

        request.session["reset_user"] = str(user["_id"])

        return redirect("user_forgot_password")

    return render(request, "user_forgot_password.html")


def user_reset_password(request):
    users_collection = settings.DB["users"]

    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("user_forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("password")

        if len(new_password) < 4:
            messages.error(request, "Password must be at least 6 characters")
            return redirect("user_reset_password")

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": hash_password(new_password)
            }}
        )

        request.session.pop("reset_user", None)

        messages.success(request, "Password updated successfully")
        return redirect("user_login")

    return render(request, "user_reset_password.html")

def user_profile(request):
    if not request.session.get("user_logged_in"):
        return redirect("user_login")

    from django.conf import settings

    users_collection = settings.DB["users"]

    user_email = request.session.get("user_email")

    user = users_collection.find_one({"email": user_email})

    return render(request, "profile.html", {
        "user": user
    })

def my_requests(request):
    if not request.session.get("user_logged_in"):
        return redirect("user_login")

    from django.conf import settings

    requests_collection = settings.DB["requests"]

    user_email = request.session.get("user_email")

    user_requests = list(requests_collection.find({
        "email": user_email
    }))

    return render(request, "my_requests.html", {
        "requests": user_requests
    })
    
# ================== USER LOGOUT ==================
def user_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect("user_login")