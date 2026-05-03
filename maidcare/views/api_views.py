from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from bson import ObjectId
from datetime import datetime

from .housekeeper_views import find_best_housekeeper


@api_view(['GET'])
def get_requests_api(request):
    requests_collection = settings.DB["requests"]

    data = list(requests_collection.find())

    # convert ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])

    return Response(data)

@api_view(['POST'])
def create_request_api(request):
    requests_collection = settings.DB["requests"]

    data = {
        "full_name": request.data.get("full_name"),
        "contact_number": request.data.get("contact_number"),
        "email": request.data.get("email"),
        "address": request.data.get("address"),
        "service_type": request.data.get("service_type"),
        "category": request.data.get("category"),
        "city": request.data.get("city"),
        "start_date": request.data.get("start_date"),
        "status": "Pending"
    }

    if not data["full_name"] or not data["contact_number"]:
        return Response({"error": "Missing fields"}, status=400)

    existing = requests_collection.find_one({
        "contact_number": data["contact_number"],
        "status": {"$in": ["Pending", "Assigned"]}
    })

    if existing:
        return Response({"error": "Duplicate request"}, status=400)
    best_hk = find_best_housekeeper(data.get("category",data.get("city")))

    if best_hk:
        data["status"] = "Assigned"
        data["assigned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["housekeeper"] = {
            "id": str(best_hk["_id"]),
            "name": best_hk["name"]
        }

    requests_collection.insert_one(data)

    return Response({"message": "Request created"})

@api_view(['GET'])
def get_housekeepers_api(request):
    hk_collection = settings.DB["housekeeper"]

    data = list(hk_collection.find())

    for item in data:
        item['_id'] = str(item['_id'])

    return Response(data)

@api_view(['POST'])
def assign_housekeeper_api(request):
    requests_collection = settings.DB["requests"]
    housekeepers_collection = settings.DB["housekeeper"]

    req_id = request.data.get("req_id")
    housekeeper_id = request.data.get("housekeeper_id")

    housekeeper = housekeepers_collection.find_one(
        {"_id": ObjectId(housekeeper_id)}
    )

    requests_collection.update_one(
        {"_id": ObjectId(req_id)},
        {"$set": {
            "status": "Assigned",
            "housekeeper": {
                "id": str(housekeeper['_id']),
                "name": housekeeper['name'],
                "contact_number": housekeeper["contact_number"],
            }
        }}
    )

    return Response({"message": "Assigned successfully"})