import os
import sqlite3

def conectar_banco():
    return sqlite3.connect('biblioteca.db')

def create_table():
    conn = conectar_banco()
    cursor = conn.cursor()

    #Criando tabela de autores
    cursor.execute(''' CREATE TABLE IF NOT EXISTS autores (
            autorID INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT)''')

    #Criando tabela de generos
    cursor.execute(''' CREATE TABLE IF NOT EXISTS generos (
            generoID INTEGER PRIMARY KEY AUTOINCREMENT ,
            nome TEXT)''')

    #Criando tabela de livros
    cursor.execute(''' CREATE TABLE IF NOT EXISTS livros (
        livroID INTEGER PRIMARY KEY AUTOINCREMENT ,
        nome TEXT NOT NULL,
        saga TEXT,
        generoID INTEGER,
        autorID INTEGER,
        editora TEXT,
        num_paginas INTEGER,
        FOREIGN KEY (autorID) REFERENCES autores (autorID),
        FOREIGN KEY (generoID) REFERENCES generos (generoID))''')

    conn.commit()
    print("Tabelas criadas com sucesso")
    conn.close()

def inserir_autores(nome_autor):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('''SELECT autorID FROM autores WHERE nome = ?''', (nome_autor,))
    result = cursor.fetchone()
    if result:
        autorID = result[0]
    else:
        cursor.execute('''INSERT INTO autores (nome) VALUES (?)''', (nome_autor,))
        autorID = cursor.lastrowid

    conn.commit()
    conn.close()
    return autorID

def buscar_generoID(nome_genero):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('''SELECT generoID FROM generos WHERE nome = ?''', (nome_genero,))
    result = cursor.fetchone()
    if result:
        genero_id = result[0]
    else:
        # Se o gênero não existir, insere um novo
        cursor.execute('''INSERT INTO generos (nome) VALUES ?''', (nome_genero,))
        genero_id = cursor.lastrowid
        conn.commit()

    conn.close()
    return genero_id

def menu():
    while True:
        print("\n1. Cadastar Livro")
        print("2. Buscar Livro")
        print("3. Editar Livro")
        print("4. Deletar Livro")
        try:
            escolha = int(input("Escolha uma opção: "))
            if escolha == 1:
                cadastrar_livro()
            elif escolha == 2:
                buscar_livro()
            elif escolha == 3:
                editar_livro()
            elif escolha == 4:
                deletar_livro()
            else:
                print("\n Número Inválido...")
        except ValueError:
            print("\nApenas números!")

def cadastrar_livro():
    conn = conectar_banco()
    cursor = conn.cursor()

    nome = input("Nome do livro: ")
    saga = input("Saga do livro: ")
    genero = input("Gênero: ")
    autor = input("Autor(a): ")
    editora = input("Editora: ")
    num_paginas = int(input("Número de Páginas: "))

    autor_id = inserir_autores(autor)
    genero_id = buscar_generoID(genero)

    cursor.execute('''
        INSERT INTO livros (nome, saga, generoID, autorID, editora, num_paginas) 
        VALUES (?, ?, ?, ?, ?, ?)''',(nome, saga, genero_id, autor_id, editora, num_paginas))

    conn.commit()
    print(f"\n O livro {nome} do autor(a) {autor} foi cadastrado com sucesso!")
    conn.close()
    voltar_menu()

def buscar_livro():
    conn = conectar_banco()
    cursor = conn.cursor()

    nome = input("\nNome do livro para busca: ")
    cursor.execute('''
        SELECT livros.livroID, livros.nome, livros.saga, generos.nome as genero, autores.nome as autor 
        FROM livros 
        INNER JOIN autores ON livros.autorID = autores.autorID 
        INNER JOIN generos ON livros.generoID = generos.generoID
        WHERE livros.nome LIKE ?''', (f"%{nome}%",))
    result = cursor.fetchall()
    if result:
        for i in result:
            print(f"ID: {i[0]}")
            print(f"Nome: {i[1]}")
            print(f"Saga: {i[2]}")
            print(f"Gênero: {i[3]}")
            print(f"Autores: {i[4]}")
    else:
        print("Nenhum Livro encontrado!")

    conn.commit()
    conn.close()
    voltar_menu()

def editar_livro():
    conn = conectar_banco()
    cursor = conn.cursor()

    nome = input("Nome do livro: ")
    cursor.execute('''
            SELECT livros.livroID, livros.nome, livros.saga, generos.nome as genero, autores.nome as autor 
            FROM livros 
            INNER JOIN autores ON livros.autorID = autores.autorID 
            INNER JOIN generos ON livros.generoID = generos.generoID
            WHERE livros.nome LIKE ?''', (f"%{nome}%",))
    result = cursor.fetchall()
    for i in result:
        print(i)

    escolha = int(input("\nQual livro editar: "))
    nome = input("\nNome do livro: ")
    saga = input("Saga: ")
    genero = input("Gênero: ")
    autor = input("Autor: ")
    editora = input("Editora: ")
    num_paginas = int(input("Número de páginas: "))

    autor_id = inserir_autores(autor)
    genero_id = buscar_generoID(genero)

    cursor.execute('''UPDATE livros SET nome = ?, saga = ?, generoID = ?, autorID = ?, editora = ?, num_paginas = ? WHERE livroID = ?''',
                   (nome, saga, genero_id, autor_id, editora, num_paginas, escolha))
    conn.commit()
    conn.close()
    voltar_menu()

def deletar_livro():
    conn = conectar_banco()
    cursor = conn.cursor()

    nome = input("Nome do livro para excluir: ")
    cursor.execute('''SELECT * FROM livros WHERE nome LIKE ?''', (f"%{nome}%",) )
    result = cursor.fetchall()
    for i in result:
        print(i)

    if len(result) > 1: #caso a busca encontre mais de uma opção
        escolha = int(input("\n Qual livro deseja excluir: "))
        try:
            escolha2 = input("\n Tem certeza que deseja excluir S/n: ")
            if escolha2 == "s":
                cursor.execute('''DELETE FROM livros WHERE livroID = ?''', (escolha,))
        except ValueError:
            print("\nValor Inválido")
            return
    else:
        try:
            escolha2 = input("\n Tem certeza que deseja excluir S/n: ")
            if escolha2 == "s":
                cursor.execute('''DELETE FROM livros WHERE nome LIKE ?''', (f"%{nome}%",))
        except ValueError:
            print("\nValor Inválido")
            return
    conn.commit()
    print("Livro deletado com sucesso!")
    conn.close()
    voltar_menu()

def voltar_menu():
    input("\nClique ENTER para voltar ao menu: ")
    menu()

def main():
    os.system("cls" if os.name == "nt" else "clear")
    create_table()
    menu()

if __name__ == "__main__":
    main()

