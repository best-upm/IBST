from app import db
from flask import render_template
from flask_login import login_required, current_user
from app.admin import bp


@bp.route('/role', methods=['GET'])
@login_required
def role():
    title='Roles'
    return render_template('roles-archive.html', title=title)
