from flask import Blueprint

bp = Blueprint('errors_blueprint', __name__, url_prefix='', template_folder='templates')

from app.errors import errors
