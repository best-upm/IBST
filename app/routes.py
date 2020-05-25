from flask import render_template, flash, redirect, url_for, request, session, send_from_directory
from app import app, db, avatars, client
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from app.forms import  EditProfile, NewPostForm, NewPollForm, LoginForm, RegisterForm
from app.functions import roles_required, role_necessary
from flask_avatars import Avatars
#from app.shedule import *	#Redis
import os, json, requests

def get_google_provider_cfg():
    return requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()

@app.route("/")
@app.route("/home")
@login_required
def  home():
	return render_template("home.html")

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
	#print(user, flush=True)
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
			if (form.avatar.data is not None):
				f=form.avatar.data
				raw_filename = avatars.save_avatar(f)
				if user.Imagenes is None:
					Imagenes=pictures()
					user.Imagenes = Imagenes
				else:
					try:
						os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], user.Imagenes.original_picture))
					except FileNotFoundError:
						pass
				user.Imagenes.original_picture=raw_filename
				db.session.commit()
				return redirect(url_for('crop'))
		return render_template('/modify_profile.html', form=form)
	else:
		return '<h1>Este no eres tu</h1>'

@app.route('/crop', methods=['GET', 'POST'])
@login_required
def crop():
	if (request.method == 'POST'):
		pictures = current_user.Imagenes
		x = request.form.get('x')
		y = request.form.get('y')
		w = request.form.get('w')
		h = request.form.get('h')
		filenames = avatars.crop_avatar(pictures.original_picture, x, y, w, h)
		if(pictures.large_picture is not None):
			try:
				os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], pictures.large_picture))
				os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], pictures.medium_picture))
				os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], pictures.small_picture))
			except FileNotFoundError:
				pass
		pictures.large_picture=filenames[2]
		pictures.medium_picture=filenames[1]
		pictures.small_picture=filenames[0]
		pictures.last_changed="Upload"
		db.session.commit()
		return redirect(url_for('profile', id=current_user.id))
	return render_template('crop.html')

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
@app.route("/login-google/callback")
def callback():
    code = request.args.get("code") # Get authorization code Google sent back to you
    google_provider_cfg = get_google_provider_cfg() # Find out what URL to hit to get tokens that allow you to ask for things on behalf of a user
    token_endpoint = google_provider_cfg["token_endpoint"]
	# Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(token_endpoint, authorization_response="https:"+request.url.split(":", 1)[1], redirect_url=app.config['BASE_URL']+"/login-google/callback", code=code)
    token_response = requests.post(token_url, headers=headers, data=body, auth=(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET']))
    client.parse_request_body_response(json.dumps(token_response.json())) # Parse the tokens!
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        family_name = userinfo_response.json()["family_name"]

    else:
        return "User email not available or not verified by Google.", 400
        #return ("<p>Hello, {}! You're logged in! Email: {}</p>""<div><p>Google Profile Picture:</p>"'<img src="{}" alt="Google profile pic"></img></div>''<a class="button" href="/logout">Logout</a>'.format(users_name, users_email, picture))

    user = User.query.filter_by(email = users_email).first()
    if user is None:
        user =User(OAUTH=True, Usuario=users_name+family_name, email=users_email, Nombre=users_name, Apellidos=family_name)
        user.set_password(unique_id)
        Imagenes=pictures()
        user.Imagenes = Imagenes
        Imagenes.picture_url=picture
        Imagenes.last_changed="URL"
        db.session.add(user)
        db.session.commit()
    elif not user.OAUTH:
        flash('Ya existe una cuenta de usuario con ese correo')
        return redirect(url_for('login'))
    elif(user.check_password(unique_id)):
        login_user(user)
    return redirect(url_for('home'))



@app.route("/login-google")
def loginGoogle():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	google_provider_cfg = get_google_provider_cfg()# Find out what URL to hit for Google login
	authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
	request_uri = client.prepare_request_uri(
        authorization_endpoint,
        #redirect_uri=request.base_url + "/callback",
        redirect_uri=app.config['BASE_URL']+"/login-google/callback",
        scope=["openid", "email", "profile"],
    )
	return redirect(request_uri)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	#print(form.validate_on_submit())
	#print(form.errors)
	if(form.validate_on_submit()):
		user = User.query.filter_by(Usuario=form.Usuario.data).first()
		if user is None or not user.check_password(form.Clave.data) or user.OAUTH:
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

@app.route('/avatars/<path:filename>')
def get_avatar(filename):
	return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)
