from app import db
from flask import render_template
from flask_login import login_required, current_user
from app.admin import bp
from app.api import bp as api_bp

@bp.route('/')
@bp.route('members', methods=['GET'])
@login_required
def members():
    title='Miembros'
    return render_template('members-archive.html', title=title)
