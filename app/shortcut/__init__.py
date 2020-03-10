from flask import Blueprint

bp = Blueprint('shortcut_blueprint', __name__, url_prefix='/url', template_folder='templates')

from app.shortcut import shortcut
from app.functions import roles_required, role_necessary
