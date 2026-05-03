from .request_views import request_service,home
from .admin_views import admin_login, admin_dashboard, logout_view,forgot_password,reset_password
from .user_views import user_login, user_register,user_logout,user_forgot_password,user_reset_password,my_requests, user_profile
from .housekeeper_views import housekeeper, edit_housekeeper, delete_housekeeper
from .management_views import category, delete_category, show_request
from .api_views import (
    get_requests_api,
    create_request_api,
    get_housekeepers_api,
    assign_housekeeper_api
)