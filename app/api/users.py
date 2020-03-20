from flask import jsonify, request, url_for, g, abort
from app import db, ma
from app.models import User, Membresia
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    id = ma.auto_field()
    Usuario= ma.auto_field()
    Nombre= ma.auto_field()
    Apellidos= ma.auto_field()
    Telefono=ma.auto_field()
    Campus=ma.auto_field()
    Escuela=ma.auto_field()
    Membresia=ma.auto_field()

    _links = ma.Hyperlinks(
        {"self": ma.AbsoluteURLFor("api_blueprint.user_detail", id="<id>"), "collection": ma.URLFor("api_blueprint.users")}
    )
user_schema =UserSchema()
users_schema = UserSchema(many=True)

@bp.route('ma/users/<id>', methods=['GET'])
def user_detail(id):
    user = User.query.get_or_404(id)
    return user_schema.dump(user)

@bp.route('ma/users', methods=['GET'])
def users():
    all_users = User.query.all()
    return users_schema.dump(all_users)

class MembresiaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Membresia
        include_fk = True
        fields = ('id', 'tipo')
    tipo = ma.auto_field()

@bp.route('usersMa', methods=['GET'])
def get_usersMa():
    user_schema=UserSchema()
    membresia_schema=MembresiaSchema()
    user = User.query.get_or_404(1)
    return user_schema.dump(user)

@bp.route('users/<int:id>', methods=['GET'])
#@token_auth.login_required
def get_user(id):
    #Returns info about a user
    return jsonify(User.query.get_or_404(id).to_dict())
@bp.route('/users', methods=['GET'])
#@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api_blueprint.get_users')
    return jsonify(data)
    #Returns a List of all users

@bp.route('/users', methods=['POST'])
def create_user():
    #Creates a new user
    data = request.get_json() or {}
    if 'Usuario' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Debe incluir Usuario, password o email')
    if User.query.filter_by(Usuario=data['Usuario']).first():
        return bad_request('Nombre de Usuario ya en uso. Cambia nombre de Usuario')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Email ya en uso, por favor usa otro email')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location']= url_for('api_blueprint.get_user', id=user.id)
    return response
@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
