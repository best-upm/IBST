from app import db
from flask import render_template
from flask_login import login_required, current_user
from app.admin import bp

@bp.route('/')
@bp.route('members', methods=['GET'])
@login_required
def members():
    return render_template('admin_template.html')
