from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database import get_usuario_por_email, insert_usuario, verificar_senha

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = get_usuario_por_email(email)

        if not usuario:
            return jsonify({'status': 'erro', 'mensagem': 'nao_cadastrado'}), 401

        if not verificar_senha(usuario['senha'], senha):
            return jsonify({'status': 'erro', 'mensagem': 'credenciais_invalidas'}), 401

        session['usuario_id'] = usuario['id']
        session['nome'] = usuario['nome']
        session['email'] = usuario['email']

        return jsonify({'status': 'sucesso', 'name': usuario['nome']})

    return render_template('login.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']

        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('auth.cadastro'))

        if get_usuario_por_email(email):
            flash('E-mail já cadastrado!', 'error')
            return redirect(url_for('auth.cadastro'))

        insert_usuario(nome, email, senha)
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html')


@auth_bp.route('/sair')
def sair():
    session.clear()
    flash('Sessão finalizada com sucesso!', 'success')
    return redirect(url_for('main.home'))
