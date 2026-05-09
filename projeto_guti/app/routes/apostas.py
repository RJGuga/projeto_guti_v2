from flask import Blueprint, render_template, request, session, jsonify
from database import insert_aposta, get_apostas_por_usuario, get_sala_por_id
from decorators import login_required

apostas_bp = Blueprint('apostas', __name__)


def _parse_aposta_payload():
    dados = request.get_json()
    if not dados:
        return None, ('Payload inválido', 400)
    return {
        'usuario_id': session.get('usuario_id'),
        'id_sala': dados.get('id_sala'),
        'time_selecionado': dados.get('time')
    }, None


@apostas_bp.route('/confirmar-aposta', methods=['POST'])
@login_required
def confirmar_aposta():
    dados, erro = _parse_aposta_payload()
    if erro:
        return jsonify({'status': 'erro', 'mensagem': erro[0]}), erro[1]
    return jsonify(dados)


@apostas_bp.route('/enviar-aposta', methods=['POST'])
@login_required
def enviar_aposta():
    dados, erro = _parse_aposta_payload()
    if erro:
        return jsonify({'status': 'erro', 'mensagem': erro[0]}), erro[1]
    insert_aposta(dados['usuario_id'], dados['id_sala'], dados['time_selecionado'])
    return jsonify({'status': 'sucesso'})


@apostas_bp.route('/apostas_por_usuario', methods=['GET'])
@login_required
def lista_apostas():
    id_usuario = session['usuario_id']
    apostas = get_apostas_por_usuario(id_usuario)

    apostas_abertas = []
    apostas_encerradas = []

    for aposta in apostas:
        sala = get_sala_por_id(aposta['id_sala'])
        if sala:
            entrada = (aposta, sala['nome_sala'])
            if sala['encerrada'] == 1:
                apostas_encerradas.append(entrada)
            else:
                apostas_abertas.append(entrada)

    return render_template(
        'apostas_por_usuario.html',
        nome_usuario=session['nome'],
        apostas_encerradas=apostas_encerradas,
        apostas_abertas=apostas_abertas
    )
