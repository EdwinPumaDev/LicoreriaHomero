
from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")

from app.routes.admin import auth
