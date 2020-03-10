from flask import render_template, flash, redirect, url_for
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from app.forms import  EditProfile, NewPostForm, NewPollForm, LoginForm, RegisterForm
from app.functions import roles_required, role_necessary
from app.shedule import *
import os, json

@app.route("/")
@app.route("/home")
@login_required
def  home():
	return render_template("home.html")

@app.route("/votaciones/newpoll", methods=['GET', 'POST'])
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def newPoll():
	form = NewPollForm()	#Titulo, Descripcion, Opciones,
	title = 'Crear nueva votacion'
	if(form.validate_on_submit()):
		poll = Poll(name=form.Titulo.data, description=form.Descripcion.data, end_date=form.end_date.data)
		options = list(form.Opciones.data.split("; "))
		for option in options:
			opcion = PollOption(option_name=option)
			poll.options.append(opcion)
		db.session.add(poll)
		db.session.commit()
		#print(options, flush=True)
		return render_template('ShowNewPoll.html', options=options)
	return render_template('Newpost.html', title=title, form=form)

@app.route("/votaciones")
@login_required
def  votaciones():
	return render_template("votaciones.html")

@app.route('/home/newpost', methods=['GET', 'POST'])
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def createNewPost():
	form = NewPostForm()
	if(form.validate_on_submit()):
		topic=Branch.query.filter_by(type=form.Rama.data).first()
		if topic is not None:
			post = Post(id_autor=current_user.id, Asunto=form.Asunto.data)
			#topic.ramas.append(post)
			topic.posts.append(post)	#Añadimos post al branch
			name=post.Asunto+".txt"
			newpost=open(name,"w+")	#Creamos un fichero nuevo por nuevo POST
			newpost.write(form.post.data)
			db.session.add(post)
			db.session.commit()

			return '<h1>Post enviado</h1>'
		return '<h1>Topic no existe, crea uno'
	return render_template('Newpost.html', form=form)

@app.route('/user')
@app.route('/user/<Usuario>', methods=['GET'])
@login_required
def userprofile(Usuario=None):
	if Usuario is not None:
		user = User.query.filter_by(Usuario=Usuario).first_or_404()
	else:
		user = User.query.get(current_user.get_id())
	print(user, flush=True)
	return render_template('render_profile.html', user=user)


@app.route('/profile/<id>', methods=['GET', 'POST'])
@login_required
def profile(id):
	if current_user.get_id()==id:
		user = User.query.get(id)
		form = EditProfile(obj=user)
		if form.validate_on_submit():
			form.populate_obj(user)
			db.session.commit()
		return render_template('/modify_profile.html', form=form)
	else:
		return '<h1>Este no eres tu</h1>'

@app.route('/admin')
@roles_required(rol=['Admin'])
def admin():
	return render_template('admin.html')

@app.route('/form/escuelas/<NombreCampus>')
def escuelas(NombreCampus):
	with open('./app/static/json/Escuelas.json') as Escuelas:
		data = json.load(Escuelas)
	for x in data['Campus']:
		if x.get('Nombre')==NombreCampus:
			EscuelasCampus= json.dumps(x.get('ETS'))
			return EscuelasCampus

#@app.route('form/user_profile/<user_id>')
#@login_required
#def user_data(user_id):

@app.route("/login", methods=['GET', 'POST'])
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


@app.route("/signIn", methods=['GET', 'POST'])
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
		return redirect(url_for('login'))
	else:
		return render_template('/Login-Register-Page/register.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	flash('Has salido con exito!')
	return redirect(url_for('login'))
