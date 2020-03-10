from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional
from app.models import User
import json, os

class LoginForm(FlaskForm):
    Usuario = StringField('Usuario', validators=[InputRequired(), Length(min=4, max=15)])
    Clave = PasswordField('Clave', validators=[InputRequired(), Length(min=8, max=30)])
    recordar =BooleanField('Recuerdame!')

class RegisterForm(FlaskForm):
    Usuario = StringField('Usuario', validators=[InputRequired(), Length(min=4, max=15)])
    Clave = PasswordField('Clave', validators=[InputRequired(), Length(min=8, max=30)])
    RClave = PasswordField('RClave', validators=[InputRequired(), EqualTo('Clave')])
    Email = EmailField('Email', validators=[InputRequired(), Email()])
    Nombre = StringField('Nombre', validators=[InputRequired()])
    Apellidos = StringField('Apellidos', validators= [InputRequired()])
    def validate_Usuario(self, Usuario):
        user=User.query.filter_by(Usuario=Usuario.data).first()
        if user is not None:
            raise ValidationError('Usa otro nombre de Usuario!')
    def validate_Email(self, Email):
        user=User.query.filter_by(email=Email.data).first()
        if user is not None:
            raise ValidationError('Usa otro correo!')

class EditProfile(FlaskForm):
    with open('./app/static/json/Escuelas.json') as Escuelas:
        data = json.load(Escuelas)
    escuelas = []
    for x in data['Campus']:
        for escuela in x.get('ETS'):
            escuelas.append(escuela)
    avatar = FileField('Subir imagen (<=3M)', validators=[FileAllowed(['jpg', 'png'], 'The file format should be .jpg or .png.')])
    Nombre = StringField('Nombre', validators=[InputRequired()])
    Apellidos = StringField('Apellidos', validators= [InputRequired()])
    Campus = SelectField('Campus', [Optional()], choices=[(f.get('Nombre'), f.get('Nombre')) for f in data['Campus']])
    Escuela = SelectField('Escuela', [Optional()], choices=[(f, f) for f in escuelas])

    #Submit = SubmitField('Enviar')
    #def validate_on_submit(self):
        #return True

class NewPostForm(FlaskForm):
    Asunto = StringField('Titulo', validators=[InputRequired(), Length(min=10, max=300)])
    Rama = StringField('Branch', validators=[InputRequired(), Length(min=1)])
    post = TextAreaField('Que te cuentas?', validators=[InputRequired(), Length(min=1)])
    Submit = SubmitField('Enviar')

class NewPollForm(FlaskForm):
    Titulo = StringField('Titulo', validators=[InputRequired(), Length(min=10, max=300)])
    Descripcion = StringField('Descripción')
    end_date = DateField('Fecha de Finalizacion', format ='%Y-%m-%d')
    Opciones = TextAreaField('Opciones (Separar por ; espacio)')
    Submit = SubmitField('Enviar')

class ChangePassForm(FlaskForm):
    Clave_Vieja = PasswordField('Clave', validators=[InputRequired(), Length(min=8, max=30)])
    new_pass = PasswordField('new_pass', validators=[InputRequired(), Length(min=8, max=30)])
    Rnew_pass = PasswordField('RClave', validators=[InputRequired(), EqualTo('new_pass')])
