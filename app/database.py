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
            paga INTEGER DEFAULT 0,
            vencedor TEXT DEFAULT NULL,
            publica INTEGER DEFAULT 0,
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carteiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER UNIQUE NOT NULL,
            saldo REAL DEFAULT 0.0,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            id_sala INTEGER,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data_hora TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_sala) REFERENCES salas (id)
        )
    ''')
    # Migrations: adiciona colunas se não existirem
    for ddl in [
        'ALTER TABLE salas ADD COLUMN paga INTEGER DEFAULT 0',
        'ALTER TABLE salas ADD COLUMN vencedor TEXT DEFAULT NULL',
        'ALTER TABLE salas ADD COLUMN publica INTEGER DEFAULT 0',
        'ALTER TABLE salas ADD COLUMN iniciada INTEGER DEFAULT 0',
    ]:
        try:
            cursor.execute(ddl)
        except Exception:
            pass  # coluna já existe

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

def insert_sala(nome_sala, time1, time2, valor, id_criador, publica=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO salas (nome_sala, time1, time2, valor, id_criador, publica) VALUES (?, ?, ?, ?, ?, ?)',
        (nome_sala, time1, time2, valor, id_criador, publica)
    )
    conn.commit()
    id_sala = cursor.lastrowid
    conn.close()
    return id_sala


def get_salas_publicas():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT s.*, u.nome AS nome_criador
        FROM salas s
        INNER JOIN usuarios u ON s.id_criador = u.id
        WHERE s.publica = 1 AND s.encerrada = 0
        ORDER BY s.id DESC
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


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
    rows = conn.execute('SELECT * FROM salas WHERE id_criador = ? ORDER BY id DESC', (id_usuario,)).fetchall()
    conn.close()
    return rows


def encerrar_sala(id_sala):
    conn = get_db_connection()
    conn.execute('UPDATE salas SET encerrada = 1 WHERE id = ?', (id_sala,))
    conn.commit()
    conn.close()


def iniciar_sala(id_sala):
    conn = get_db_connection()
    conn.execute('UPDATE salas SET iniciada = 1 WHERE id = ?', (id_sala,))
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
        ORDER BY a.id DESC
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


def get_apostadores_por_time(id_sala, time):
    """Retorna lista de id_usuario que apostaram no time informado."""
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT id_usuario FROM apostas WHERE id_sala = ? AND time_selecionado = ?',
        (id_sala, time)
    ).fetchall()
    conn.close()
    return [r['id_usuario'] for r in rows]


def creditar_premio(id_usuario, id_sala, valor):
    """Credita o prêmio na carteira do usuário e registra em transacoes."""
    conn = get_db_connection()
    _garantir_carteira(conn, id_usuario)
    conn.execute('UPDATE carteiras SET saldo = saldo + ? WHERE id_usuario = ?', (valor, id_usuario))
    conn.execute(
        'INSERT INTO transacoes (id_usuario, id_sala, tipo, valor) VALUES (?, ?, ?, ?)',
        (id_usuario, id_sala, 'premio', valor)
    )
    conn.commit()
    conn.close()


def marcar_sala_paga(id_sala):
    """Marca a sala como já distribuída para evitar duplo pagamento."""
    conn = get_db_connection()
    conn.execute('UPDATE salas SET paga = 1 WHERE id = ?', (id_sala,))
    conn.commit()
    conn.close()


def salvar_vencedor(id_sala, vencedor):
    """Persiste o time vencedor na sala."""
    conn = get_db_connection()
    conn.execute('UPDATE salas SET vencedor = ? WHERE id = ?', (vencedor, id_sala))
    conn.commit()
    conn.close()


def sala_ja_paga(id_sala):
    conn = get_db_connection()
    row = conn.execute('SELECT paga FROM salas WHERE id = ?', (id_sala,)).fetchone()
    conn.close()
    return bool(row and row['paga'])


# ── Carteira ──────────────────────────────────────────────────────────────────

def _garantir_carteira(conn, id_usuario):
    """Cria a carteira do usuário se ainda não existir (dentro de uma conexão aberta)."""
    conn.execute(
        'INSERT OR IGNORE INTO carteiras (id_usuario, saldo) VALUES (?, 0.0)',
        (id_usuario,)
    )


def get_saldo(id_usuario):
    conn = get_db_connection()
    _garantir_carteira(conn, id_usuario)
    conn.commit()
    row = conn.execute('SELECT saldo FROM carteiras WHERE id_usuario = ?', (id_usuario,)).fetchone()
    conn.close()
    return row['saldo'] if row else 0.0


def depositar(id_usuario, valor):
    conn = get_db_connection()
    _garantir_carteira(conn, id_usuario)
    conn.execute('UPDATE carteiras SET saldo = saldo + ? WHERE id_usuario = ?', (valor, id_usuario))
    conn.execute(
        'INSERT INTO transacoes (id_usuario, tipo, valor) VALUES (?, ?, ?)',
        (id_usuario, 'deposito', valor)
    )
    conn.commit()
    conn.close()


def retirar(id_usuario, valor):
    conn = get_db_connection()
    _garantir_carteira(conn, id_usuario)
    row = conn.execute('SELECT saldo FROM carteiras WHERE id_usuario = ?', (id_usuario,)).fetchone()
    saldo_atual = row['saldo'] if row else 0.0
    if saldo_atual < valor:
        conn.close()
        return False, 'Saldo insuficiente'
    conn.execute('UPDATE carteiras SET saldo = saldo - ? WHERE id_usuario = ?', (valor, id_usuario))
    conn.execute(
        'INSERT INTO transacoes (id_usuario, tipo, valor) VALUES (?, ?, ?)',
        (id_usuario, 'retirada', valor)
    )
    conn.commit()
    conn.close()
    return True, 'ok'


def debitar_aposta(id_usuario, id_sala, valor):
    """Debita o valor da aposta da carteira. Retorna (True,'ok') ou (False, motivo)."""
    conn = get_db_connection()
    _garantir_carteira(conn, id_usuario)
    row = conn.execute('SELECT saldo FROM carteiras WHERE id_usuario = ?', (id_usuario,)).fetchone()
    saldo_atual = row['saldo'] if row else 0.0
    if saldo_atual < valor:
        conn.close()
        return False, 'Saldo insuficiente para realizar esta aposta'
    conn.execute('UPDATE carteiras SET saldo = saldo - ? WHERE id_usuario = ?', (valor, id_usuario))
    conn.execute(
        'INSERT INTO transacoes (id_usuario, id_sala, tipo, valor) VALUES (?, ?, ?, ?)',
        (id_usuario, id_sala, 'aposta', valor)
    )
    conn.commit()
    conn.close()
    return True, 'ok'


def get_transacoes(id_usuario):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT t.*, s.nome_sala
        FROM transacoes t
        LEFT JOIN salas s ON t.id_sala = s.id
        WHERE t.id_usuario = ?
        ORDER BY t.id DESC
        LIMIT 50
    ''', (id_usuario,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


