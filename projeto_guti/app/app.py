"""
Entry point da aplicação.
Para rodar: python app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
