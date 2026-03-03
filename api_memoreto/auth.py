from flask import Blueprint, request, session, g
from .db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/validausuario', methods=['POST'])
def valida_usuario():
    data = request.get_json()
    correo = data.get('usuario')
    password = data.get('pass')
    
    db = get_db()
    
    # Buscar al usuario en la base de datos
    user = db.execute(
        'SELECT * FROM usuario WHERE correo = ?', (correo,)
    ).fetchone()

    # Validamos usuario y contraseña (en texto plano por ahora para pruebas)
    if user is None or user['password'] != password:
        return {"valido": False, "error": "Credenciales incorrectas"}

    # Si es correcto, iniciamos sesión guardando el id_usuario
    session.clear()
    session['user_id'] = user['id_usuario']
    
    return {
        "valido": True, 
        "id_usuario": user['id_usuario'], 
        "rol": user['rol']
    }

# Función para mantener la sesión del usuario (como la de tu profe)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM usuario WHERE id_usuario = ?', (user_id,)
        ).fetchone()