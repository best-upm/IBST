from flask import Blueprint

bp = Blueprint('poll_blueprint', __name__, url_prefix='/poll', template_folder='templates')

from app.polls import polls, PollForms
from app.functions import roles_required, role_necessary
