from flask import Blueprint, render_template, session

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    nome_usuario = session.get('nome')
    criar_sala = nome_usuario is not None
    return render_template('home.html', nome_usuario=nome_usuario, criar_sala=criar_sala)
