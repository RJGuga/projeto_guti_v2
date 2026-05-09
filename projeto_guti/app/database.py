import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


def get_db_connection():
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_sala TEXT NOT NULL,
            id_criador INTEGER NOT NULL,
            time1 TEXT NOT NULL,
            time2 TEXT NOT NULL,
            valor INTEGER NOT NULL,
            encerrada INTEGER DEFAULT 0,
            FOREIGN KEY (id_criador) REFERENCES usuarios (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            id_sala INTEGER NOT NULL,
            time_selecionado TEXT NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_sala) REFERENCES salas (id)
        )
    ''')
    conn.commit()
    conn.close()


# ── Usuários ──────────────────────────────────────────────────────────────────

def insert_usuario(nome, email, senha):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
        (nome, email, generate_password_hash(senha))
    )
    conn.commit()
    conn.close()


def get_usuario_por_email(email):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_usuario_por_id(id_usuario):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM usuarios WHERE id = ?', (id_usuario,)).fetchone()
    conn.close()
    return dict(row) if row else None


def verificar_senha(hash_senha, senha_plain):
    return check_password_hash(hash_senha, senha_plain)


# ── Salas ─────────────────────────────────────────────────────────────────────

def insert_sala(nome_sala, time1, time2, valor, id_criador):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO salas (nome_sala, time1, time2, valor, id_criador) VALUES (?, ?, ?, ?, ?)',
        (nome_sala, time1, time2, valor, id_criador)
    )
    conn.commit()
    id_sala = cursor.lastrowid
    conn.close()
    return id_sala


def get_sala_por_id(id_sala):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM salas WHERE id = ?', (id_sala,)).fetchone()
    conn.close()
    return row


def get_sala_detalhada_por_id(id_sala):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT s.*, u.nome AS nome_criador,
               COUNT(a.id) AS apostas_time1,
               COUNT(b.id) AS apostas_time2
        FROM salas s
        INNER JOIN usuarios u ON s.id_criador = u.id
        LEFT JOIN apostas a ON s.id = a.id_sala AND a.time_selecionado = s.time1
        LEFT JOIN apostas b ON s.id = b.id_sala AND b.time_selecionado = s.time2
        WHERE s.id = ?
        GROUP BY s.id
    ''', (id_sala,)).fetchone()
    conn.close()
    return row


def get_salas_criadas_por_usuario(id_usuario):
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM salas WHERE id_criador = ?', (id_usuario,)).fetchall()
    conn.close()
    return rows


def encerrar_sala(id_sala):
    conn = get_db_connection()
    conn.execute('UPDATE salas SET encerrada = 1 WHERE id = ?', (id_sala,))
    conn.commit()
    conn.close()


# ── Apostas ───────────────────────────────────────────────────────────────────

def insert_aposta(id_usuario, id_sala, time_selecionado):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO apostas (id_usuario, id_sala, time_selecionado) VALUES (?, ?, ?)',
        (id_usuario, id_sala, time_selecionado)
    )
    conn.commit()
    conn.close()


def get_apostas_por_usuario(id_usuario):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT a.*, s.nome_sala
        FROM apostas a
        INNER JOIN salas s ON a.id_sala = s.id
        WHERE a.id_usuario = ?
    ''', (id_usuario,)).fetchall()
    conn.close()
    return rows


def get_quantidade_apostas_por_sala(id_sala):
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM apostas WHERE id_sala = ?', (id_sala,)).fetchone()[0]
    conn.close()
    return count


def get_quantidade_apostas_por_time(id_sala, time):
    conn = get_db_connection()
    count = conn.execute(
        'SELECT COUNT(*) FROM apostas WHERE id_sala = ? AND time_selecionado = ?',
        (id_sala, time)
    ).fetchone()[0]
    conn.close()
    return count
