from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField, TimeField, DateTimeField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional, ValidationError
from datetime import date, datetime

class NewPollForm(FlaskForm):
    name = StringField('Titulo', validators=[InputRequired(), Length(min=10, max=300)])
    description = StringField('Descripción')
    start_date = DateField('Fecha de Inicio', format ='%Y-%m-%d', default=date.today)
    start_time = TimeField('Hora de Inicio')
    end_date = DateField('Fecha de Finalización', format ='%Y-%m-%d', default=date.today)
    end_time = TimeField('Hora de Finalización')
    Opciones = TextAreaField('Opciones (Separar por ; espacio)', validators=[InputRequired()])
    Submit = SubmitField('Enviar')
    def validate_start_date(FlaskForm, self):
        if (self.data < date.today()):
            raise ValidationError('La fecha de Inicio no puede ser anterior a la de hoy')
    def validate_end_date(FlaskForm, self):
        if (self.data < FlaskForm.start_date.data):
            raise ValidationError('La fecha de Finalizacion no puede ser anterior a la de Inicio')
    def validate_Opciones(FlaskForm, self):
        options = list(self.data.split("; "))
        if (len(options) < 2):
            raise ValidationError('Oh I see... Uno de los mios! Decisiones faciles para que no se lo tengan que pensar mucho')
