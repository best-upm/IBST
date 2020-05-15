from datetime import datetime, date, timedelta
import base64, os
import json
#from imgur-uploader import imgur-uploader
from app import db, login
from flask_login import UserMixin
from flask import jsonify, current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


@login.user_loader
def load_user(id):
    #return User.query.get(int(id))
    return User.query.get(id)

Rol = db.Table('Roles', db.Column('id', db.Integer, db.ForeignKey('user.id')), db.Column('id_Membresia', db.Integer, db.ForeignKey('membresia.id')))
#Topic = db.Table('Topic' db.Column('id_post', db.Integer, db.ForeignKey('post.id_post')), db.Column('id_branch', db.Integer, db.ForeignKey('branch.id_branch')))
Topic = db.Table('Topic', db.Column('id_post', db.Integer, db.ForeignKey('post.id_post')), db.Column('id_branch', db.Integer, db.ForeignKey('branch.id_branch')))
#La tabla PollOptions y UserVote, tienen una relacion M:M, son multiples votos a multiples opciones
#Creamos una tabla intermedia que las relacione. La llamare: voto_opcion, o la traduccion en ingles option_vote
option_vote = db.Table('option_vote', db.Column('id_option', db.Integer, db.ForeignKey('poll_option.id_option')), db.Column('user', db.Integer, db.ForeignKey('user.id')))
users_polls = db.Table('users_polls', db.Column('id_poll', db.Integer, db.ForeignKey('poll.id_poll')), db.Column('user', db.Integer, db.ForeignKey('user.id')))
#users_polls is usefull for searching the polls that the user has filled already.
#class User(UserMixin, db.Model):
class User(db.Model, PaginatedAPIMixin, UserMixin):
    #__tablename__='Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    idType = db.Column(db.String(4)) #Esto esta por la implementacion de Google Auth. Hay un tipo de cuentas que no tiene clave
    Usuario = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    Nombre = db.Column(db.String(30))
    Apellidos = db.Column(db.String(200))
    Telefono = db.Column(db.String(15))
    Campus = db.Column(db.String(30))
    Escuela = db.Column(db.String(50))
    #Imagen = db.Column(db.String(50))
    #Twitter = db.Column(db.String(50))
    Imagenes = db.relationship('pictures', backref='user', uselist=False)
    Membresia = db.relationship('Membresia', secondary=Rol, backref=db.backref('Miembros', lazy='dynamic'))
    votes = db.relationship('PollOption', secondary=option_vote, backref=db.backref('votos', lazy='dynamic'))
    filled_polls = db.relationship('Poll', secondary=users_polls, backref=db.backref('users_polls', lazy='dynamic'))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration=db.Column(db.DateTime)
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        if self.idType == "OAUTH":  #AGUJERO!!!
            return True
        return check_password_hash(self.password_hash, password)
    def check_role(self, role):
        id_membresia =Membresia.query.filter_by(tipo=role).first()
        return id_membresia in self.Miembros
    def check_neccesary_role(self, roles):
        for rol in roles:
            id_membresia=Membresia.query.filter_by(tipo=rol).first()
            if id_membresia in current_user.Miembros:
                return True
        return False
    def __repr__(self):
        return '<User {}>'.format(self.Usuario)

    def to_dict(self, include_email=False, include_avaliable_roles=False, include_picture=False):
        member=[]
        for x in self.Membresia:
            member.append(x.to_dict())
        data={
        'id':self.id,
        'Usuario':self.Usuario,
        'Nombre': self.Nombre,
        'Apellidos': self.Apellidos,
        'Telefono': self.Telefono,
        'Campus': self.Campus,
        'Escuela': self.Escuela,
        #'Membresia': member,
        }
        if include_email:
            data['email']= self.email
        if include_avaliable_roles:
            membresias=Membresia.query.all()
            roles=[]
            for x in membresias:
                roles.append(x.serialize(self.check_role(x.tipo)))
            data['Membresia']= roles
        else:
            data['Membresia']=member
        if include_picture:
            if self.Imagenes != None:
                data['pictures']=self.Imagenes.get_picture()
            else:
                data['pictures']=None
        return data

    def from_dict(self, data, new_user=False):
        for field in ['Usuario', 'email', 'Nombre', 'Apellidos', 'Telefono']:
            if field in data:
                setattr(self, field, data[field])
            if new_user and 'password' in data:
                self.set_password(data['password'])


class pictures(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    original_picture = db.Column(db.String(50))
    large_picture = db.Column(db.String(50))
    medium_picture = db.Column(db.String(50))
    small_picture = db.Column(db.String(50))
    Twitter_user_picture = db.Column(db.String(50))
    picture_url = db.Column(db.String(300))
    last_changed = db.Column(db.String(20))
    def get_picture(self, size=None):
        data={}
        if(size == "small"):
            if self.last_changed == "Upload":
                data = {'small_picture':"/avatars/"+self.small_picture}
            elif self.last_changed == "URL":
                data = {'URL':self.picture_url+"=s50"}
            elif self.last_changed == "Twitter":
                data= {'Twitter':self.Twitter_user_picture}
        elif(size == "medium"):
            if self.last_changed == "Upload":
                data = {'small_picture':"/avatars/"+self.medium_picture}
            elif self.last_changed == "URL":
                data = {'URL':self.picture_url+"=s100"}
            elif self.last_changed == "Twitter":
                data= {'Twitter':self.Twitter_user_picture}
        elif(size == "big"):
            if self.last_changed == "Upload":
                data = {'small_picture':"/avatars/"+self.small_picture}
            elif self.last_changed == "URL":
                data = {'URL':self.picture_url+"=s250"}
            elif self.last_changed == "Twitter":
                data= {'Twitter':self.Twitter_user_picture}
        if self.last_changed == "Upload":
            data = {
            'original_picture':"/avatars/"+self.original_picture,
            'large_picture':"/avatars/"+self.large_picture,
            'medium_picture':"/avatars/"+self.medium_picture,
            'small_picture':"/avatars/"+self.small_picture
            }
        elif self.last_changed == "URL":
            data = {'URL':self.picture_url}
        elif self.last_changed == "Twitter":
            data= {'Twitter':self.Twitter_user_picture}
        return data

class Membresia(db.Model):
    #__tablename__='Roles'
    id = db.Column(db.Integer(), primary_key=True)
    tipo = db.Column(db.String(30), unique=True)
    Usuarios = db.relationship('User', secondary=Rol, backref=db.backref('Miembros', lazy= 'dynamic'))
    def __repr__(self):
        return '{}'.format(self.tipo)
    #def toJSON(self):
        #return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    def serialize(self, state):
        return {
            'id':self.id,    #
            'tipo':self.tipo,   #
            'state': state
        }
    def to_dict(self):
        data={
        'id': self.id,
        'tipo': self.tipo
        }
        return data

class Post(db.Model):
    id_post=db.Column(db.Integer(), primary_key=True)
    id_autor=db.Column(db.Integer(),db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    Asunto = db.Column(db.String(300))
    #Branch = db.Column(db.Integer(), db.ForeignKey('branch.id_branch'), nullable=False)
    #Branch = db.relationship('Post', secondary=Topic, backref=db.backref('ramas', lazy= 'dynamic'))

    def __repr__(self):
        return '<Post {}>'.format(self.Asunto)

class Branch(db.Model):
    id_branch=db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(30), unique=True)
    posts = db.relationship("Post", secondary=Topic, backref=db.backref('posts', lazy='dynamic'))
    def __repr__(self):
        return '<Branch {}>'.format(self.type)

class Poll(PaginatedAPIMixin, db.Model):
    id_poll = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(300))
    start_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    options = db.relationship("PollOption", back_populates="parent_poll")
    id_creator = db.Column(db.Integer(), db.ForeignKey('user.id'))
    voters = db.relationship('User', secondary=users_polls, backref=db.backref('users_polls', lazy='dynamic'))
    def __repr__(self):
        return '<Votacion {}'.format(self.name)
    def to_dict(self):
        #print(self.name, flush=True)
        #print(self.options, flush=True)
        list=[]
        for x in self.options:
            list.append(x.option_name)
        data = {
        'id': self.id_poll,
        'name': self.name,
        'description': self.description,
        'end_date': self.end_date,
        'options': list
        }
        return data

class PollOption(db.Model):
    __tablename__='poll_option'
    id_option=db.Column(db.Integer(), primary_key=True)
    id_parent_poll = db.Column(db.Integer(), db.ForeignKey('poll.id_poll'))
    parent_poll= db.relationship("Poll", back_populates="options")
    option_name = db.Column(db.String(100))     #De cara al futuro, pensar si se puede incluir objetos como opciones en las votaciones
    votes = db.relationship("User", secondary=option_vote, backref=db.backref('usuario', lazy='dynamic'))
    #votos = db.relationship()
    def __repr__(self):
        return '<Opcion> {}'.format(self.option_name)
    def to_dict(self):
        data={
        'id':self.id_option,
        'name': self.option_name
        }
        return data

class URL_Shortener(db.Model):
    __tablename__='url_shortener'
    #id_shortcut = db.Column(db.Integer(), primary_key=True)
    shortcutlink = db.Column(db.String(20), index=True, unique=True, primary_key=True)
    link = db.Column(db.String(2048))
    expiration_date = db.Column(db.DateTime, index=True)
    def __repr__(self):
        return 'Link acortado: {}, redirige a: {} y expira el:{}'.format(self.shortcutlink, self.link, self.expiration_date)
    def to_dict(self):
        data={
        'shortcutlink':self.shortcutlink,
        'link':self.link,
        'expiration_date':self.expiration_date
        }
        return data
    #def set_expiration_date(self):
        #This funtion sets a cronjob to delete the record

def delete_expired_objects(clase):
    data=clase.query.all()
    for link in data:
        if link.expiration_date < datetime.today():
            db.session.delete(link)
        db.session.commit()
