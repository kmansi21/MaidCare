from django.shortcuts import render, redirect
from django.conf import settings
from bson import ObjectId
from django.contrib import messages
from django.conf import settings


def housekeeper(request):
    hk_collection = settings.DB["housekeeper"]
    cat_collection = settings.DB["category"]
    if request.method == "POST":
        data = {
            "maidId": request.POST.get("maidId"),
            "name": request.POST.get("name"),
            "mobile": request.POST.get("mobile"),
            "email": request.POST.get("email"),
            "category": {
                "id": request.POST.get("category"),
                "name": cat_collection.find_one(
                    {"_id": ObjectId(request.POST.get("category"))}
                )["name"]
            },
            "experience": int(request.POST.get("experience")),
            "address": request.POST.get("address"),
            "city": request.POST.get("city"),
            "available": True
        }

        hk_collection.insert_one(data)
        messages.success(request, "Housekeeper added successfully")
        return redirect("housekeeper")

 
    housekeepers = list(hk_collection.find())
    categories = list(cat_collection.find())


    for hk in housekeepers:
        hk["id"] = str(hk["_id"])

    for c in categories:
        c["id"] = str(c["_id"])

    return render(request, "housekeeper.html", {
        "housekeepers": housekeepers,
        "categories": categories
    })



def delete_housekeeper(request, id):
    hk_collection = settings.DB["housekeeper"]
    hk_collection.delete_one({"_id": ObjectId(id)})
    messages.error(request, "Housekeeper deleted successfully")
    return redirect("housekeeper")

def edit_housekeeper(request, id):
    hk_collection = settings.DB["housekeeper"]
    cat_collection = settings.DB["category"]

    if request.method == "POST":
        category_id = request.POST.get("category")

        category_data = None
        if category_id:
            category_data = cat_collection.find_one({"_id": ObjectId(category_id)})

        updated_data = {
            "maidId": request.POST.get("maidId"),
            "name": request.POST.get("name"),
            "mobile": request.POST.get("mobile"),
            "email": request.POST.get("email"),
            "experience": request.POST.get("experience"),
            "address": request.POST.get("address"),
             "city": request.POST.get("city"),
        }
        if category_data:
            updated_data["category"] = {
                "id": category_id,
                "name": category_data["name"]
            }

        hk_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": updated_data}
        )

        messages.success(request, "Housekeeper updated successfully")
        return redirect("housekeeper")
    
def is_time_conflict(existing_from, existing_to, new_from, new_to):
    return not (new_to <= existing_from or new_from >= existing_to)
    
MAX_TASKS = 5

def find_best_housekeeper(category_name, new_from, new_to,user_city):
    hk_collection = settings.DB["housekeeper"]
    requests_collection = settings.DB["requests"]

    candidates = list(hk_collection.find({
        "category.name": category_name,
        "city": user_city
    }))

    valid_candidates = []

    for hk in candidates:
        assigned_requests = list(requests_collection.find({
            "housekeeper.id": str(hk["_id"]),
            "status": "Assigned"
        }))

        # ❌ skip if overload
        if len(assigned_requests) >= MAX_TASKS:
            continue

        is_available = True

        for req in assigned_requests:
            if is_time_conflict(
                req["work_shift_from"],
                req["work_shift_to"],
                new_from,
                new_to
            ):
                is_available = False
                break

        if is_available:
            hk["workload"] = len(assigned_requests)
            valid_candidates.append(hk)

    if not valid_candidates:
        return None

    valid_candidates.sort(
        key=lambda x: (x["workload"], -int(x.get("experience", 0)))
    )

    return valid_candidates[0]