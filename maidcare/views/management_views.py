from django.shortcuts import render, redirect
from django.conf import settings
from bson import ObjectId
from django.contrib import messages
from datetime import datetime


def category(request):
    categories_collection = settings.DB["category"]

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            categories_collection.insert_one({"name": name})
            messages.success(request, "Category added successfully")
        else:
            messages.error(request, "Category name is required")

        return redirect("category")

    categories = list(categories_collection.find())
    for c in categories:
        c["id"] = str(c["_id"])
    return render(request, "category.html", {
        "categories": categories
    })

def delete_category(request, id):
    if request.method == "POST":
        categories_collection = settings.DB["category"]
        categories_collection.delete_one({"_id": ObjectId(id)})
        messages.error(request, "Category deleted successfully")
    return redirect("category")

def show_request(request):
    requests_collection = settings.DB["requests"]
    housekeepers_collection = settings.DB["housekeeper"]
    categories_collection = settings.DB["category"]
    categories = list(categories_collection.find())
    for c in categories:
        c["id"] = str(c["_id"])
        
    housekeepers_data = list(housekeepers_collection.find())
    for hk in housekeepers_data:
        hk['id'] = str(hk['_id'])

    if request.method == "POST":
        req_id = request.POST.get("req_id")
        action = request.POST.get("action")

        if action == "assign":
            housekeeper_id = request.POST.get("housekeeper_id")
            if housekeeper_id:
                housekeeper = housekeepers_collection.find_one({"_id": ObjectId(housekeeper_id)})
                requests_collection.update_one(
                    {"_id": ObjectId(req_id)},
                    {"$set": {
                        "status": "Assigned", 
                        "assigned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "housekeeper": {
                            "id": str(housekeeper['_id']),
                            "name": housekeeper.get('name', '')
                        }
                    }}
                )
        elif action == "cancel":
            req = requests_collection.find_one({"_id": ObjectId(req_id)})

            # free housekeeper
            if req.get("housekeeper"):
                hk_id = req["housekeeper"]["id"]
                housekeepers_collection.update_one(
                    {"_id": ObjectId(hk_id)},
                    {"$set": {"available": True}}
                )

            requests_collection.update_one(
                {"_id": ObjectId(req_id)},
                {"$set": {"status": "Cancelled"}}
            )

        return redirect("hiring_requests")

    requests_data = list(requests_collection.find().sort("start_date", -1))
    for req in requests_data:
        req['id'] = str(req['_id'])
        req['customer_name'] = req.get('full_name', '')
        req['mobile'] = req.get('contact_number', '')
        req['category_name'] = req.get('category', {}).get('name', '')
        req['housekeeper'] = req.get('housekeeper', None)
        req['shift_time'] = f"{req.get('work_shift_from', '')} - {req.get('work_shift_to', '')}"
        # Normalize status correctly
        status_map = {
            "Pending": "new",
            "Assigned": "assigned",  # match exactly what is stored in DB
            "Cancelled": "cancelled"
        }
        req_status = req.get('status', 'Pending')
        req['status_normalized'] = status_map.get(req_status, 'new')
        req['created_at'] = req.get('start_date', '')
        req['assignment_reason'] = req.get('assignment_reason', '')
    return render(request, "hiring_requests.html", {
        "requests": requests_data,
        "housekeepers": housekeepers_data,
        "categories": categories
    })