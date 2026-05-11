from flask import Blueprint, render_template, request, session, jsonify
from ..database import get_saldo, depositar, retirar, get_transacoes
from ..decorators import login_required

carteira_bp = Blueprint('carteira', __name__)


@carteira_bp.route('/carteira')
@login_required
def carteira():
    id_usuario = session['usuario_id']
    saldo = get_saldo(id_usuario)
    transacoes = get_transacoes(id_usuario)
    voltar = request.args.get('voltar', None)
    return render_template('carteira.html', saldo=saldo, transacoes=transacoes, nome_usuario=session['nome'], voltar=voltar)


@carteira_bp.route('/carteira/saldo', methods=['GET'])
@login_required
def carteira_saldo():
    saldo = get_saldo(session['usuario_id'])
    return jsonify({'saldo': saldo})


@carteira_bp.route('/carteira/depositar', methods=['POST'])
@login_required
def carteira_depositar():
    try:
        valor = float(request.form.get('valor', 0))
        if valor <= 0:
            return jsonify({'status': 'erro', 'mensagem': 'Valor inválido'}), 400
        depositar(session['usuario_id'], valor)
        novo_saldo = get_saldo(session['usuario_id'])
        return jsonify({'status': 'sucesso', 'saldo': novo_saldo})
    except (ValueError, TypeError):
        return jsonify({'status': 'erro', 'mensagem': 'Valor inválido'}), 400


@carteira_bp.route('/carteira/retirar', methods=['POST'])
@login_required
def carteira_retirar():
    try:
        valor = float(request.form.get('valor', 0))
        if valor <= 0:
            return jsonify({'status': 'erro', 'mensagem': 'Valor inválido'}), 400
        ok, msg = retirar(session['usuario_id'], valor)
        if not ok:
            return jsonify({'status': 'erro', 'mensagem': msg}), 400
        novo_saldo = get_saldo(session['usuario_id'])
        return jsonify({'status': 'sucesso', 'saldo': novo_saldo})
    except (ValueError, TypeError):
        return jsonify({'status': 'erro', 'mensagem': 'Valor inválido'}), 400
