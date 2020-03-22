from flask import jsonify, request, url_for, g, abort
from app import db, ma
from app.models import User, Membresia
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth

"""The function of /api-role is to provide a way to create new roles. Also you should be able to give a role to a Member
It should do things, I dont remember"""
@bp.route("/roles", methods=['GET'])
def get_roles():
    """This method returns a set of roles"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(Membresia.query, page, per_page, 'api_blueprint.get_roles')
    return jsonify(data)

@bp.route('/users_roles/<int:id>', methods=['GET'])
def get_roles_Settings_of_User(id):
    user=User.query.get_or_404(id)
    data=user.to_dict(include_avaliable_roles=True)
    data['self']='/api/users_roles/'+str(id)
    return jsonify(data)

@bp.route('/users_roles/<int:id>', methods=['PUT'])
def set_role_to_User(id):
    user=User.query.get(id)
    data = request.get_json() or {}
    x=data['Membresia']
    for i in x:
        print(i['state'], flush= True)
        if (i['state'] and not (user.check_role(i['tipo']))):
            membresia=Membresia.query.get(i['id'])
            user.Membresia.append(membresia)
        elif((user.check_role(i['tipo']) and not i['state'])):
            membresia=Membresia.query.get(i['id'])
            user.Membresia.remove(membresia)
    #print(x, flush=True);
    db.session.commit()
    #print(membresias, flush=True);
    return jsonify("done")

@bp.route('/users_roles/<int:id>', methods=['DELETE'])
def delete_role_from_User(id):
    user=User.query.get_or_404(id)
    data = request.get_json() or {}
    print(data, flush=True)
