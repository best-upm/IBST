from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional
from app.models import User
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
