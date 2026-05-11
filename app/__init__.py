import os

from flask import Flask, session
from .config import DevelopmentConfig
from .database import create_tables, get_saldo


def create_app(config_class=DevelopmentConfig):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    with app.app_context():
        create_tables()

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.salas import salas_bp
    from .routes.apostas import apostas_bp
    from .routes.chat import chat_bp
    from .routes.carteira import carteira_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(salas_bp)
    app.register_blueprint(apostas_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(carteira_bp)

    @app.context_processor
    def inject_saldo():
        if session.get('usuario_id'):
            return {'saldo_carteira': get_saldo(session['usuario_id'])}
        return {'saldo_carteira': None}

    return app
