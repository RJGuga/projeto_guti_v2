from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from ..database import (
    insert_sala, get_sala_por_id, get_sala_detalhada_por_id,
    get_salas_criadas_por_usuario, encerrar_sala,
    get_quantidade_apostas_por_sala, get_quantidade_apostas_por_time,
    get_usuario_por_id
)
from ..decorators import login_required

salas_bp = Blueprint('salas', __name__)


@salas_bp.route('/sala', methods=['GET', 'POST'])
@login_required
def criar_sala():
    if request.method == 'POST':
        try:
            nome_sala = request.form['nome_sala']
            time1 = request.form['time1']
            time2 = request.form['time2']
            valor = request.form['valor']
            id_criador = session['usuario_id']
            id_sala = insert_sala(nome_sala, time1, time2, valor, id_criador)
            return redirect(url_for('salas.sala', id_sala=id_sala))
        except Exception as e:
            return f"Erro durante a criação da sala: {e}", 500
    return render_template('criar_sala.html', nome_criador=session['nome'])


@salas_bp.route('/sala/<int:id_sala>', methods=['GET', 'POST'])
@login_required
def sala(id_sala):
    sala = get_sala_detalhada_por_id(id_sala)
    if not sala:
        return "Sala não encontrada", 404

    titulo = f"{sala['nome_sala']} criada por: {sala['nome_criador']}"
    apostas_time1 = get_quantidade_apostas_por_time(id_sala, sala['time1'])
    apostas_time2 = get_quantidade_apostas_por_time(id_sala, sala['time2'])

    return render_template(
        'sala.html',
        sala=sala,
        titulo=titulo,
        nome_criador=sala['nome_criador'],
        valor=sala['valor'],
        apostas_time1=apostas_time1,
        apostas_time2=apostas_time2
    )


@salas_bp.route('/sala/<int:id_sala>/convidado', methods=['GET'])
@login_required
def sala_convidado(id_sala):
    sala = get_sala_por_id(id_sala)
    if not sala:
        return "Sala não encontrada", 404

    criador = get_usuario_por_id(sala['id_criador'])
    nome_criador = criador['nome'] if criador else ''

    return render_template(
        'sala_convidado.html',
        sala=sala,
        nome_criador=nome_criador,
        valor_sala=sala['valor'],
        titulo=sala['nome_sala'],
        id_sala=id_sala
    )


@salas_bp.route('/sala/<int:id_sala>/encerrar_apostas', methods=['POST'])
@login_required
def encerrar_apostas(id_sala):
    encerrar_sala(id_sala)
    quantidade = get_quantidade_apostas_por_sala(id_sala)
    return jsonify({'quantidade_apostas': quantidade})


@salas_bp.route('/sala/<int:id_sala>/quantidade_apostas', methods=['GET'])
def quantidade_apostas(id_sala):
    return jsonify({'quantidade_apostas': get_quantidade_apostas_por_sala(id_sala)})


@salas_bp.route('/sala/<int:id_sala>/resultado', methods=['GET', 'POST'])
@login_required
def resultado(id_sala):
    if request.method == 'POST':
        vencedor = request.form.get('time-selection')
        return redirect(url_for('salas.resultado', id_sala=id_sala, vencedor=vencedor))

    sala = get_sala_por_id(id_sala)
    if not sala:
        return "Sala não encontrada", 404

    criador = get_usuario_por_id(sala['id_criador'])
    nome_criador = criador['nome'] if criador else ''
    vencedor = request.args.get('vencedor')
    apostas_time1 = get_quantidade_apostas_por_time(id_sala, sala['time1'])
    apostas_time2 = get_quantidade_apostas_por_time(id_sala, sala['time2'])
    quantidade_apostas = get_quantidade_apostas_por_sala(id_sala)

    return render_template(
        'resultado.html',
        nome_criador=nome_criador,
        sala=sala,
        quantidade_apostas=quantidade_apostas,
        apostas_time1=apostas_time1,
        apostas_time2=apostas_time2,
        vencedor=vencedor
    )


@salas_bp.route('/sala/<int:id_sala>/apostas_realizadas', methods=['GET'])
@login_required
def apostas_realizadas(id_sala):
    sala = get_sala_por_id(id_sala)
    if not sala:
        return "Sala não encontrada", 404

    usuario = get_usuario_por_id(session['usuario_id'])
    apostas_time1 = get_quantidade_apostas_por_time(id_sala, sala['time1'])
    apostas_time2 = get_quantidade_apostas_por_time(id_sala, sala['time2'])
    quantidade_apostas = get_quantidade_apostas_por_sala(id_sala)

    return render_template(
        'apostas_realizadas.html',
        nome_criador=usuario['nome'],
        sala=sala,
        apostas_time1=apostas_time1,
        apostas_time2=apostas_time2,
        quantidade_apostas=quantidade_apostas
    )


@salas_bp.route('/salas_criadas', methods=['GET'])
@login_required
def salas_criadas():
    id_usuario = session['usuario_id']
    todas = get_salas_criadas_por_usuario(id_usuario)
    salas_abertas = [s for s in todas if s['encerrada'] == 0]
    salas_encerradas = [s for s in todas if s['encerrada'] == 1]

    return render_template(
        'salas_criadas.html',
        nome_usuario=session['nome'],
        salas_abertas=salas_abertas,
        salas_encerradas=salas_encerradas
    )
