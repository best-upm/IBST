from app import db, app, migrate
from app.models import *

def setup_db():

    user=User(Usuario="GLaDos", email=os.environ.get('SERVER_EMAIL'), Nombre="Caroline")
    user.set_password("noviembre")
    admin=Membresia(tipo="Admin")
    baby=Membresia(tipo="Baby")
    observer=Membresia(tipo="Observer")
    full=Membresia(tipo="Full")
    user.Membresia.append(admin)
    user.Membresia.append(baby)
    user.Membresia.append(observer)
    user.Membresia.append(full)
    db.session.add(admin)
    db.session.add(observer)
    db.session.add(baby)
    db.session.add(full)
    db.session.add(user)

setup_db()
