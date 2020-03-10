from flask import Blueprint

bp = Blueprint('mail_blueprint', __name__, url_prefix='/mail', template_folder='templates')

from app.mail import mail
from app.functions import roles_required, role_necessary
