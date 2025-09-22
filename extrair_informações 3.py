import sqlite3
import re

def conecta_bd():
    conn = sqlite3.connect("partidas.bd")
    cursor = conn.cursor()

    # Cria a tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            cod INTEGER PRIMARY KEY AUTOINCREMENT,
            Evento TEXT,
            Local_do_jogo TEXT,
            Data TEXT,
            Rodada TEXT,
            Brancas TEXT,
            Pretas TEXT,
            Resultado TEXT,
            Controle_tempo TEXT,
            Codigo_ECO TEXT,
            Abertura TEXT,
            Rating_Brancas TEXT,
            Rating_Pretas TEXT,
            Titulo_Brancas TEXT,
            Titulo_Pretas TEXT,
            Terminacao TEXT,
            Tabuleiro TEXT,
            Partida TEXT
        )
    """)
    return conn, cursor

def salvar_partida(dados, partida_pgn):
    conn, cursor = conecta_bd()
    cursor.execute("""
        INSERT INTO partidas (
            Evento, Local_do_jogo, Data, Rodada, Brancas, Pretas,
            Resultado, Controle_tempo, Codigo_ECO, Abertura,
            Rating_Brancas, Rating_Pretas, Titulo_Brancas, Titulo_Pretas,
            Terminacao, Tabuleiro, Partida
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (*dados, partida_pgn))
    conn.commit()
    conn.close()

def importar_pgn(arquivo):
    with open(arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # divide várias partidas dentro do mesmo arquivo
    partidas = conteudo.strip().split("\n\n\n")

    for partida in partidas:
        # pega tags PGN
        tags = dict(re.findall(r'\[(\w+)\s+"([^"]+)"\]', partida))

        dados = [
            tags.get("Event", ""),
            tags.get("Site", ""),
            tags.get("Date", tags.get("UTCDate", "")),
            tags.get("Round", ""),
            tags.get("White", ""),
            tags.get("Black", ""),
            tags.get("Result", ""),
            tags.get("TimeControl", ""),
            tags.get("ECO", ""),
            tags.get("Opening", ""),
            tags.get("WhiteElo", ""),
            tags.get("BlackElo", ""),
            tags.get("WhiteTitle", ""),
            tags.get("BlackTitle", ""),
            tags.get("Termination", ""),
            tags.get("Board", ""),
        ]

        # extrai somente os lances (a partir do "1.")
        match = re.search(r'1\. .*', partida, re.S)
        somente_partida = match.group(0).strip() if match else ""
        salvar_partida(dados, somente_partida)
        print(f"✅ Partida salva: {tags.get('White', '?')} x {tags.get('Black', '?')}")

# Exemplo de uso
importar_pgn("novo.pgn")
