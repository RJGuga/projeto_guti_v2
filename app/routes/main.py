from flask import Blueprint, render_template, session
from ..database import get_salas_publicas

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    nome_usuario = session.get('nome')
    criar_sala = nome_usuario is not None
    salas_publicas = get_salas_publicas()
    return render_template('home.html', nome_usuario=nome_usuario, criar_sala=criar_sala, salas_publicas=salas_publicas)
