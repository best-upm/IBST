from flask import render_template, flash, redirect, jsonify
from app import app, db
from flask_login import login_required
from app.functions import roles_required, role_necessary
from app.shortcut import bp
from app.models import URL_Shortener, delete_expired_objects
from datetime import date, datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional, ValidationError

class NewCutDownURLForm(FlaskForm):
    link = StringField('Link', validators=[InputRequired(), Length(min=10, max=2048)])
    shortcutlink = StringField('Link corto', validators=[InputRequired(), Length(min=4, max=20)])
    expiration_date = DateField('Fecha de Expiracion', format ='%Y-%m-%d', default=(date.today()+timedelta(days=30)))
    def validate_shortcutlink(FlaskForm, self):
        link = URL_Shortener.query.filter_by(shortcutlink=self.data).first()
        if link is not None:
            raise ValidationError('Este Link acortado ya esta siendo usado y esta operativo')

@bp.route('/create', methods=['GET', 'POST']) #Quizas create deberia ser simplemente "/" y ya. Ni que fuera a haber otro link por aqui...
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def newShortCut():
    #delete_expired_links()
    #delete_expired_objects(clase=URL_Shortener())
    title = 'Crear nuevo URL acortado'
    CutDownURL=URL_Shortener()
    cutdownURLForm = NewCutDownURLForm(obj=CutDownURL)
    if (cutdownURLForm.validate_on_submit()):
        cutdownURLForm.populate_obj(CutDownURL)
        db.session.add(CutDownURL)
        db.session.commit()
        #flash ('Exito, se ha creado el link acortado  {}'.format('localhost:5000/url/'+cutdownURLForm.shortcutlink.data))  #BASE_URL+'/url/'+cutdownURLForm.shortcutlink
        flash ('Exito, se ha creado el link acortado  {}'.format(app.config['BASE_URL']+'/url/'+cutdownURLForm.shortcutlink.data))  #BASE_URL+'/url/'+cutdownURLForm.shortcutlink
        #return 'URL Creado'
    return render_template('CreateNewShortURL.html', title=title, form=cutdownURLForm)

@bp.route('/<string:shortcutlink>', methods=['GET'])
def redirectToURL(shortcutlink=None):
    link_object = URL_Shortener.query.get(shortcutlink)
    if (link_object is None):
        return 'Baya, baya!!!'  #Deberia redirigir a alguna pagina bonica, bestmadrid.org por ejemplo
    return redirect(link_object.link, code=302)

@bp.route('/get_urls', methods=['GET'])
def getAllUrls():
    #This has to return a list of shortened urls, with their redirect paths
    urls = URL_Shortener.query.all()
    data = {
    'url': [x.to_dict() for x in urls]
    }
    return data

@bp.route('/delete_url/<string:shortcutlink>', methods=["DELETE"])
#@token_auth.login_required  #Deberia tener tamb en algun sitio prohibicion para eliminar
def deleteUrl(shortcutlink=None):
    try:
        url_d = URL_Shortener.query.get_or_404(shortcutlink)
        db.session.delete(url_d)
        db.session.commit()
        data={'success':'true'}
    except:
        data={'success':'false'}
    finally:
        return jsonify(data)
def delete_expired_links():
    data=URL_Shortener.query.all()
    for link in data:
        if link.expiration_date < datetime.today():
            db.session.delete(link)
        db.session.commit()
