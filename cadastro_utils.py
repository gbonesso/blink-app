from kivy import platform
import os
from pathlib import Path


def get_storage_path():
    if platform == "android":
        from android import mActivity
        context = mActivity.getApplicationContext()
        result = context.getExternalFilesDir(None)  # don't forget the argument
        if result:
            storage_path = str(result.toString())
    else:
        storage_path = "."
    return storage_path


def cadastro(usuario, senha, perfil_medico):
    # Verifica se existe algo no campo de usuário
    if len(usuario) == 0:
        return "Insira Usuário"
    elif len(senha) == 0:
        return "Insira Senha"
    # Verifica se o campo de usuário é maior do que o limite de caracteres
    elif len(usuario) > 10:
        return "Limite de caracteres para usuário excedido"
    elif len(senha) > 10:
        return "Limite de caracteres para senha excedido"
    elif consulta_usuario(usuario):
        return "Usuário já está cadastrado..."
    else:
        # Acessa o banco de dados e cadastra o novo usuário e sua senha
        file_path = os.path.join(get_storage_path(), "banco_de_dados.txt")
        meu_arquivo = Path(file_path)
        if not meu_arquivo.exists():
            file = open(file_path, "w")
            file.close()
        banco_dados = open(file_path, "a")
        perfil = "MEDICO" if perfil_medico else "PACIENTE"
        banco_dados.write(usuario + "," + senha + "," + perfil)
        banco_dados.write("\n")
        banco_dados.close()
        return "Cadastro Realizado!"



def consulta_usuario(usuario):
    # abre o arquivo txt com as informações de logins
    file_path = os.path.join(get_storage_path(), "banco_de_dados.txt")
    meu_arquivo = Path(file_path)
    if meu_arquivo.exists():
        banco_dados = open(file_path, "r")  # lê linha por linha no banco de dados
        for lines in banco_dados:
            cadastros = lines.split(",")  # Separa a string pela virgula (cria uma lista)
            if cadastros[0] == usuario:
                banco_dados.close()
                return True
        banco_dados.close()
    return False


def consulta_senha_usuario(usuario):
    # abre o arquivo txt com as informações de logins
    file_path = os.path.join(get_storage_path(), "banco_de_dados.txt")
    banco_dados = open(file_path, "r")  # lê linha por linha no banco de dados
    for lines in banco_dados:
        cadastros = lines.split(",")  # Separa a string pela virgula (cria uma lista)
        if cadastros[0] == usuario:
            senha = cadastros[1]
            banco_dados.close()
            return True, senha
    banco_dados.close()
    return False, None


def login(usuario, senha):
    # Verifica se existe algo no campo de usuário
    if len(usuario) == 0:
        return "Insira Usuário"
    elif len(senha) == 0:
        return "Insira Senha"
    # Verifica se o campo de usuário é maior do que o limite de caracteres
    elif len(usuario) > 10:
        return "Limite de caracteres para usuário excedido"
    elif len(senha) > 10:
        return "Limite de caracteres para senha excedido"
    else:
        existe, senha_cadastrada = consulta_senha_usuario(usuario)
        print('existe: {} senha_cadastrada: {} senha: {}'.format(existe, senha_cadastrada.rstrip(), senha))
        if not existe:
            return "Usuário não existe"
        else:
            if senha != senha_cadastrada.rstrip():  # rstrip() -> Elimina a quebra de linha da senha...
                return "Senha inválida"
            else:
                return "Login efetuado com sucesso!"