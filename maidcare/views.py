from django.shortcuts import render , redirect
from django.conf import settings
from bson import ObjectId
from django.contrib import messages




def request_service(request):
    requests_collection = settings.DB["requests"]
    categories_collection = settings.DB["category"]
    services_collection = settings.DB["services"]

    if request.method == "POST":
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

        requests_collection.insert_one(data)
        messages.success(request, "Service request submitted successfully!")
        return redirect("/request/#request")  

    # GET request part
    categories = list(categories_collection.find())
    for cat in categories:
        cat["id"] = str(cat["_id"])

    services = list(services_collection.find({"active": True}))

    return render(request, "index.html", {
        "categories": categories,
        "services": services
    })
    
def admin_login(request):
    admins_collection = settings.DB["admins"]

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        admin = admins_collection.find_one({
            "username": username,
            "password": password
        })

        if admin:
            request.session["admin_logged_in"] = True
            request.session["admin_username"] = username
            return redirect("/admindashboard/")
        else:
            return render(request, "admin_login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "admin_login.html")

def admin_dashboard(request):
    if not request.session.get("admin_logged_in"):
        return redirect("/adminlogin/")
    requests_collection = settings.DB["requests"]
    housekeepers_collection = settings.DB["housekeeper"]
    total_requests = requests_collection.count_documents({})
    new_requests = requests_collection.count_documents({"status": "Pending"})
    total_housekeepers = housekeepers_collection.count_documents({})
    pending_requests = requests_collection.count_documents({"status": "Pending"})

    return render(request, "admin_dashboard.html", {
        "admin_name": request.session.get("admin_username"),
        "total_requests": total_requests,
        "new_requests": new_requests,
        "total_housekeepers": total_housekeepers,
        "pending_requests": pending_requests
    })
    
def category(request):
    categories_collection = settings.DB["category"]

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            categories_collection.insert_one({"name": name})
            messages.success(request, "Category added successfully")
        else:
            messages.error(request, "Category name is required")

        return redirect("/category/")

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
    return redirect("/category/")




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
            "experience": request.POST.get("experience"),
            "address": request.POST.get("address")
        }

        hk_collection.insert_one(data)
        messages.success(request, "Housekeeper added successfully")
        return redirect("/housekeeper/")

 
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
    return redirect("/housekeeper/")

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
        return redirect("/housekeeper/")
    


def show_request(request):
    requests_collection = settings.DB["requests"]
    housekeepers_collection = settings.DB["housekeeper"]

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
                        "status": "Assigned",  # Capital A to match template normalization
                        "housekeeper": {
                            "id": str(housekeeper['_id']),
                            "name": housekeeper.get('name', '')
                        }
                    }}
                )
        elif action == "cancel":
            requests_collection.update_one(
                {"_id": ObjectId(req_id)},
                {"$set": {"status": "Cancelled"}}
            )

        return redirect("/hiring/")

    requests_data = list(requests_collection.find().sort("start_date", -1))
    for req in requests_data:
        req['id'] = str(req['_id'])
        req['customer_name'] = req.get('full_name', '')
        req['mobile'] = req.get('contact_number', '')
        req['category_name'] = req.get('category', {}).get('name', '')
        req['housekeeper'] = req.get('housekeeper', None)

        # Normalize status correctly
        status_map = {
            "Pending": "new",
            "Assigned": "assigned",  # match exactly what is stored in DB
            "Cancelled": "cancelled"
        }
        req_status = req.get('status', 'Pending')
        req['status_normalized'] = status_map.get(req_status, 'new')
        req['created_at'] = req.get('start_date', '')

    return render(request, "hiring_requests.html", {
        "requests": requests_data,
        "housekeepers": housekeepers_data
    })
    

def logout_view(request):
    request.session.flush()  
    messages.success(request, "You have successfully logged out.")
    return redirect('/adminlogin/')  