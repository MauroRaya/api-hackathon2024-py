import sqlite3

class Evento:
    def __init__(self, nome, data, localidade, cidade, preco_minimo, preco_maximo, descricao, link_compra, link_origem, imagem, id=None):
        self.id = id
        self.nome = nome
        self.data = data
        self.localidade = localidade
        self.cidade = cidade
        self.preco_minimo = preco_minimo
        self.preco_maximo = preco_maximo
        self.descricao = descricao
        self.link_compra = link_compra
        self.link_origem = link_origem
        self.imagem = imagem
    
    def to_dict(self):
        return self.__dict__
    

def initialize_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS eventos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        data TEXT,
                        localidade TEXT,
                        cidade TEXT,
                        preco_minimo TEXT,
                        preco_maximo TEXT,
                        descricao TEXT,
                        link_compra TEXT,
                        link_origem TEXT,
                        imagem TEXT)''')
    conn.commit()
    conn.close()


def save_events(evento):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT id FROM eventos WHERE nome = ? AND data = ? AND localidade = ?''',
                   (evento.nome, evento.data, evento.localidade))
    existing_event = cursor.fetchone()

    if existing_event:
        print(f'Evento {evento.nome} já existe no banco de dados. Ignorando inserção')
    else:
        cursor.execute('''INSERT INTO eventos 
                    (nome, data, localidade, cidade, preco_minimo, preco_maximo, descricao, link_compra, link_origem, imagem) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (evento.nome, evento.data, evento.localidade, evento.cidade, evento.preco_minimo, evento.preco_maximo, evento.descricao, evento.link_compra, evento.link_origem, evento.imagem))
        
        print(f'Evento {evento.nome} inserido no banco de dados')
            
    conn.commit()
    conn.close()


def get_events():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM eventos')
    rows = cursor.fetchall()

    eventos = [Evento(*row[1:], id=row[0]).to_dict() for row in rows]

    conn.close()
    return eventos


def delete_all_events():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM eventos')
    print('Eventos antigos deletados com sucesso')
    conn.commit()
    conn.close()