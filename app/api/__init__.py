from flask import Blueprint

bp = Blueprint('api_blueprint', __name__, url_prefix='/api', template_folder='templates')

from app.api import users, tokens, errors
