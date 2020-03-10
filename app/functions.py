from app import db
from app.models import Membresia
from flask_login import current_user
from flask import redirect, abort
import functools

def roles_required(rol):
    #Debido a la incompatibilidad entre flask_login y flask_user, y mi preferencia a usar flask_login, tengo que hacer un decorator que restrinja zonas
    #User.query.filter_by(rol=rol.self).first()
    #Doc para acordarme: Se le pasa una lista, y comprueba que cumpla con TODOS los roles dentro de la lista
    def decorator_roles(func):
        @functools.wraps(func)
        def wrapper_roles_required(*args, **kwargs):
            for roles in rol:
                id_membresia =Membresia.query.filter_by(tipo=roles).first()    #Encontramos id Membresia
                if not id_membresia in current_user.Miembros:
                    return abort(403)
            value = func(*args, **kwargs)
            return value
        return wrapper_roles_required
    return decorator_roles

def role_necessary(rol):
    #Este caso es para aquellos que solo deben cumplir uno, o mas de los roles, pero no necesariamente todos
    def decorator_role(func):
        @functools.wraps(func)
        def wrapper_role_necessary(*args, **kwargs):
            for roles in rol:
                id_membresia=Membresia.query.filter_by(tipo=roles).first()
                if id_membresia in current_user.Miembros:
                    return func(*args, **kwargs)
            return abort(403)
        return wrapper_role_necessary
    return decorator_role
