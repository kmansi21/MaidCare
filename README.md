# MaidCare Management System

MaidCare is a web-based admin dashboard and service management system for managing hiring requests for housekeepers. The platform allows multiple users to submit service requests, which are handled by admins and assigned to available housekeepers.

## Features

### User Requests
Users can submit service requests with details such as:
- Service Type
- Work Shift
- Service Category

### Admin Dashboard
- Secure admin login
- View all service requests
- Assign housekeepers to requests
- Cancel requests
- Monitor request status

### Housekeeper Management
- Add housekeepers
- Edit housekeeper details
- Delete housekeepers
- Manage service categories for each housekeeper

### Dynamic Status
Each request can have one of the following statuses:
- New
- Assigned
- Cancelled

## Database Relationship

Many-to-One Relationship:
- Multiple service requests can exist.
- Each request is assigned to one housekeeper.
- One housekeeper can handle multiple requests.

## Tech Stack

- Backend: Django
- Database: MongoDB (NoSQL)
- Frontend: HTML, CSS, Bootstrap, JavaScript

## How It Works

1. Users submit service requests with their details.
2. Admins log in to the dashboard to view all requests.
3. Admins assign a housekeeper to a request or cancel it.
4. The request status is updated dynamically in the database.
5. Each housekeeper can manage multiple requests, while each request is linked to one housekeeper.

##  Project Screenshots

###  Home Page
<img width="1920" height="1080" alt="Home Page" src="https://github.com/user-attachments/assets/47a38d55-1679-4e61-a519-c81cf628e5f8" />

---

### Service Request Form
<img width="1920" height="1080" alt="Request Form" src="https://github.com/user-attachments/assets/39c3753f-fc8d-4241-87ac-c85f186ef225" />

---

### Admin Dashboard
<img width="1920" height="1080" alt="Admin Dashboard 1" src="https://github.com/user-attachments/assets/baae599f-c18e-4428-a5f3-9496aa64dd5e" />

<img width="1920" height="1080" alt="Admin Dashboard 2" src="https://github.com/user-attachments/assets/163be241-74c4-417d-9483-774b84469099" />

---
