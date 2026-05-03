from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from collections import defaultdict
from datetime import datetime
import json
from bson import ObjectId
import hashlib


# ================== HELPER ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_admin(request):
    return request.session.get("role") == "admin"


# ================== ADMIN LOGIN ==================
def admin_login(request):
    admins_collection = settings.DB["admins"]

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        admin = admins_collection.find_one({
            "username": username,
            "password": hash_password(password)   # ✅ FIXED
        })

        if admin:
            request.session["admin_logged_in"] = True
            request.session["admin_username"] = username
            request.session["role"] = "admin"
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "admin_login.html")


# ================== ADMIN DASHBOARD ==================
def admin_dashboard(request):
    if not is_admin(request):
        return redirect('admin_login')

    requests_collection = settings.DB["requests"]
    housekeepers_collection = settings.DB["housekeeper"]

    data = list(requests_collection.find())

    total_requests = len(data)
    assigned = len([r for r in data if r.get("status") == "Assigned"])
    cancelled = len([r for r in data if r.get("status") == "Cancelled"])
    pending = len([r for r in data if r.get("status") == "Pending"])

    total_housekeepers = housekeepers_collection.count_documents({})

    # Category Data
    category_data = {}
    for r in data:
        cat = r.get("category", {}).get("name", "Unknown")
        category_data[cat] = category_data.get(cat, 0) + 1

    # Date Data
    date_data = defaultdict(int)
    for r in data:
        date_str = r.get("start_date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted = date_obj.strftime("%d %b")
                date_data[formatted] += 1
            except:
                pass

    date_data = dict(sorted(
        date_data.items(),
        key=lambda x: datetime.strptime(x[0], "%d %b")
    ))

    most_used_category = max(category_data, key=category_data.get) if category_data else "N/A"

    return render(request, "admin_dashboard.html", {
        "admin_name": request.session.get("admin_username"),
        "total_requests": total_requests,
        "total_housekeepers": total_housekeepers,
        "assigned": assigned,
        "cancelled": cancelled,
        "pending": pending,
        "category_data": json.dumps(category_data),
        "date_data": json.dumps(date_data),
        "most_used_category": most_used_category
    })


# ================== FORGOT PASSWORD ==================
def forgot_password(request):
    admins_collection = settings.DB["admins"]

    if request.method == "POST":
        identifier = request.POST.get("identifier")

        admin = admins_collection.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier}
            ]
        })

        if not admin:
            messages.error(request, "Admin not found")
            return redirect('admin_forgot_password')

        request.session["reset_admin"] = str(admin["_id"])
        return redirect('admin_reset_password')

    return render(request, "forgot_password.html")


# ================== RESET PASSWORD ==================
def reset_password(request):
    admins_collection = settings.DB["admins"]

    admin_id = request.session.get("reset_admin")

    if not admin_id:
        return redirect('admin_forgot_password')

    admin = admins_collection.find_one({"_id": ObjectId(admin_id)})

    if not admin:
        return redirect('admin_forgot_password')

    if request.method == "POST":
        new_username = request.POST.get("username")
        new_email = request.POST.get("email")
        new_password = request.POST.get("password")

        # 🔴 Basic Validation
        if not new_username or not new_email:
            messages.error(request, "Username and Email are required")
            return redirect('admin_reset_password')

        # 🔴 Check duplicate username
        existing = admins_collection.find_one({
            "username": new_username,
            "_id": {"$ne": ObjectId(admin_id)}
        })

        if existing:
            messages.error(request, "Username already taken")
            return redirect('admin_reset_password')

        update_data = {}

        if new_username != admin.get("username"):
            update_data["username"] = new_username

        if new_email != admin.get("email"):
            update_data["email"] = new_email

        if new_password:
            if len(new_password) < 6:
                messages.error(request, "Password must be at least 6 characters")
                return redirect('admin_reset_password')
            update_data["password"] = hash_password(new_password)

        if update_data:
            admins_collection.update_one(
                {"_id": ObjectId(admin_id)},
                {"$set": update_data}
            )
            messages.success(request, "Credentials updated successfully")
        else:
            messages.info(request, "No changes made")

        request.session.pop("reset_admin", None)
        return redirect('admin_login')

    return render(request, "reset_password.html", {
        "admin": admin
    })


# ================== LOGOUT ==================
def logout_view(request):
    request.session.flush()
    messages.success(request, "You have successfully logged out.")
    return redirect('admin_login')