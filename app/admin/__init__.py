from flask import Blueprint

bp = Blueprint('admin_blueprint', __name__, url_prefix='/Admin', template_folder='templates')
from app.admin import members, roles
