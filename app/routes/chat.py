from flask import Blueprint, request, session, jsonify

chat_bp = Blueprint('chat', __name__)

_chat_global = []
_chat_por_sala = []


@chat_bp.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify([{'username': m['username'], 'message': m['message']} for m in _chat_global])


@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    message = request.form.get('message', '').strip()
    if not message:
        return jsonify({'status': 'erro', 'mensagem': 'Mensagem vazia'}), 400
    _chat_global.append({'username': session.get('nome', 'Anônimo'), 'message': message})
    return jsonify({'status': 'sucesso'})


@chat_bp.route('/get_messages_por_sala', methods=['GET'])
def get_messages_por_sala():
    id_sala = request.args.get('id_sala')
    data = [{'username': m['username'], 'message': m['message']} for m in _chat_por_sala if m['id_sala'] == id_sala]
    return jsonify(data)


@chat_bp.route('/send_message_por_sala', methods=['POST'])
def send_message_por_sala():
    message = request.form.get('message', '').strip()
    id_sala = request.form.get('id_sala')
    if not message or not id_sala:
        return jsonify({'status': 'erro', 'mensagem': 'Dados inválidos'}), 400
    _chat_por_sala.append({'username': session.get('nome', 'Anônimo'), 'message': message, 'id_sala': id_sala})
    return jsonify({'status': 'sucesso'})
