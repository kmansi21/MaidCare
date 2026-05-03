from django.shortcuts import render, redirect
from django.conf import settings
from bson import ObjectId
from django.contrib import messages
from datetime import datetime

from .housekeeper_views import find_best_housekeeper

def home(request):
    from django.conf import settings

    category_collection = settings.DB["category"]
    categories = list(category_collection.find())

    return render(request, "index.html", {
        "categories": categories
    })
def request_service(request):
    requests_collection = settings.DB["requests"]
    categories_collection = settings.DB["category"]
    services_collection = settings.DB["services"]

    if request.method == "POST":
        if not request.session.get("user_logged_in"):
            messages.error(request, "Please login to submit request")
            return redirect("user_login")
        def convert_to_24(hour, period):
            hour = int(hour)
            if period == "PM" and hour != 12:
                hour += 12
            if period == "AM" and hour == 12:
                hour = 0
            return f"{hour:02d}:00"

        category_id = request.POST.get("category")
        category_data = None
        if category_id:
            category_data = categories_collection.find_one({"_id": ObjectId(category_id)})

        data = {
            "full_name": request.POST.get("full_name"),
            "contact_number": request.POST.get("contact_number"),
            
            "email": request.POST.get("email"),
            "address": request.POST.get("address"),
            "city": request.POST.get("city"),
            "service_type": request.POST.get("service_type"),
            "category": {
                "id": str(category_data["_id"]),
                "name": category_data["name"]
            } if category_data else None,
            "work_shift_from": convert_to_24(request.POST.get("from_hour"), request.POST.get("from_period")),
            "work_shift_to": convert_to_24(request.POST.get("to_hour"), request.POST.get("to_period")),
            "start_date": request.POST.get("start_date"),
            "additional_notes": request.POST.get("additional_notes"),
            "status": "Pending"
        }
        # ================= DUPLICATE CHECK HERE =================
        existing_request = requests_collection.find_one({
            "full_name": data["full_name"],
            "contact_number": data["contact_number"],
            "start_date": data["start_date"],
            "category.name": data["category"]["name"] if data["category"] else None,
            "status": {"$in": ["Pending", "Assigned"]}
        })

        if existing_request:
            messages.error(request, "You already have an active request for this service!")
            return redirect("/#request")

    # ================= AUTO ASSIGN LOGIC =================
        best_hk = find_best_housekeeper(
            data["category"]["name"],
            data["work_shift_from"],
            data["work_shift_to"],
            data["city"]
        )

        if best_hk:
            data["status"] = "Assigned"
            data["assigned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["housekeeper"] = {
                "id": str(best_hk["_id"]),
                "name": best_hk["name"]
            }

            messages.success(request, "Housekeeper assigned successfully!")

        else:
            data["status"] = "Pending"
            data["assignment_reason"] = "No housekeeper available in this city"

            messages.warning(request, "No housekeeper available right now. We will assign soon.")

        

        requests_collection.insert_one(data)
        return redirect("/#request")  

    # GET request part
    categories = list(categories_collection.find())
    for cat in categories:
        cat["id"] = str(cat["_id"])

    services = list(services_collection.find({"active": True}))

    return render(request, "index.html", {
        "categories": categories,
        "services": services
    })