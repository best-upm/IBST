from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional, ValidationError
from datetime import date, datetime

class NewPollForm(FlaskForm):
    name = StringField('Titulo', validators=[InputRequired(), Length(min=10, max=300)])
    description = StringField('Descripción')
    start_date = DateField('Fecha de Inicio', format ='%Y-%m-%d', default=date.today)
    end_date = DateField('Fecha de Finalizacion', format ='%Y-%m-%d', default=date.today)
    Opciones = TextAreaField('Opciones (Separar por ; espacio)')
    Submit = SubmitField('Enviar')
    def validate_start_date(FlaskForm, self):
        if (self.data < date.today()):
            raise ValidationError('La fecha de Inicio no puede ser anterior a la de hoy')
    def validate_end_date(FlaskForm, self):
        if (self.data < FlaskForm.start_date.data):
            raise ValidationError('La fecha de Finalizacion no puede ser anterior a la de Inicio')
