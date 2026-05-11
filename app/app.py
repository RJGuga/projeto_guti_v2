"""
Entry point da aplicação.
Para rodar a partir da raiz do projeto: python -m app.app
"""
import os
import sys

# Garante que a raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8000)
