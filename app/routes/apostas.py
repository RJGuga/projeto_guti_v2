from flask import Blueprint, render_template, request, session, jsonify
from ..database import insert_aposta, get_apostas_por_usuario, get_sala_por_id, debitar_aposta, get_saldo, get_quantidade_apostas_por_sala, get_quantidade_apostas_por_time
from ..decorators import login_required

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

    sala = get_sala_por_id(dados['id_sala'])
    if not sala:
        return jsonify({'status': 'erro', 'mensagem': 'Sala não encontrada'}), 404

    saldo = get_saldo(dados['usuario_id'])
    if saldo < float(sala['valor']):
        return jsonify({'status': 'erro', 'mensagem': 'Saldo insuficiente'}), 400

    return jsonify({'status': 'sucesso'})


@apostas_bp.route('/enviar-aposta', methods=['POST'])
@login_required
def enviar_aposta():
    dados, erro = _parse_aposta_payload()
    if erro:
        return jsonify({'status': 'erro', 'mensagem': erro[0]}), erro[1]

    sala = get_sala_por_id(dados['id_sala'])
    if not sala:
        return jsonify({'status': 'erro', 'mensagem': 'Sala não encontrada'}), 404

    ok, msg = debitar_aposta(dados['usuario_id'], dados['id_sala'], float(sala['valor']))
    if not ok:
        return jsonify({'status': 'erro', 'mensagem': msg}), 400

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
            sala = dict(sala)
            if sala['encerrada'] == 1:
                premio_ganho = None
                if sala.get('vencedor') and aposta['time_selecionado'] == sala['vencedor']:
                    qtd_total = get_quantidade_apostas_por_sala(sala['id'])
                    qtd_vencedores = get_quantidade_apostas_por_time(sala['id'], sala['vencedor'])
                    if qtd_vencedores and qtd_vencedores > 0:
                        valor_liquido = qtd_total * float(sala['valor']) * 0.9
                        premio_ganho = round(valor_liquido / qtd_vencedores, 2)
                apostas_encerradas.append((aposta, sala, premio_ganho))
            else:
                apostas_abertas.append((aposta, sala))

    return render_template(
        'apostas_por_usuario.html',
        nome_usuario=session['nome'],
        apostas_encerradas=apostas_encerradas,
        apostas_abertas=apostas_abertas
    )
