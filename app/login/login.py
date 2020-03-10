from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, UserMixin
from app import db
from app.login import bp
from app.login.forms import LoginForm, RegisterForm
from app.models import *
from flask_login import current_user, login_user, logout_user, login_required

@bp.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	#print(form.validate_on_submit())
	#print(form.errors)
	if(form.validate_on_submit()):
		user = User.query.filter_by(Usuario=form.Usuario.data).first()
		if user is None or not user.check_password(form.Clave.data):
			flash('Usuario o Clave invalida')
			#return redirect(url_for('login'))
			return render_template('/Login-Register-Page/login.html', form=form)
		login_user(user, remember=form.recordar.data)
		return redirect(url_for('home'))
	return render_template('/Login-Register-Page/login.html', form=form)


@bp.route("/signIn", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegisterForm()
	if(form.validate_on_submit()):
		user =User(Usuario=form.Usuario.data, email=form.Email.data, Nombre=form.Nombre.data, Apellidos=form.Apellidos.data)
		user.set_password(form.Clave.data)
		db.session.add(user)
		db.session.commit()
		flash('Bienvenido a BEST Madrid!')
		return redirect(url_for('login_blueprint.login'))
	else:
		return render_template('/Login-Register-Page/register.html', form=form)

@bp.route('/logout')
def logout():
	logout_user()
	flash('Has salido con exito!')
	return redirect(url_for('login_blueprint.login'))
