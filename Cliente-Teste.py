from socket import *
import json
from time import sleep
import sys

MODO_DEPURACAO = 1

estagios_forca = [
        "  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========", 
        "  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========", 
        "  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========", 
        "  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========", 
        "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========", 
        "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========", 
        "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========", 
        "  +---+\n  |   |\n  X   |\n /|\\  |\n / \\  |\n      |\n=========", 
    ]

dicio_indexador = {
    "tipo": "indexador",
    "mensagem": ""
}

dicio_num_palavras_disponiveis = {
    "tipo": "num_palavras"
}

dicio_comecar_jogo = {
    "tipo": "comecar_jogo"
}

dicio_jogo_da_forca = {
    "tipo": "jogo_da_forca"
}

dicio_num_chances_fixo = {
    "tipo": "num_chances_fixo"
}

dicio_tentativa = {
    "tipo": "tentativa",
    "mensagem": ""
}

dicio_encerrar_conexao = {
    "tipo": "encerrar_conexao"
}

def imprimir_depuracao(mensagem):
    if (MODO_DEPURACAO):
        print(mensagem)

def imprimir_letras_utilizadas(lista):
    print("Letras utilizadas: ", end="")
    for letra_utilizada in lista:
        print(f"{letra_utilizada} | ", end="")
    print()
    
def imprimir_palavra_censurada(palavra_censurada):
    print("Palavra: ", end="")
    for letra_palavra in palavra_censurada:
        print(f"{letra_palavra} ", end="")
    print()

def bool_letra_repetida(letra_entrada, lista_letras_utilizadas):
    for letra_utilizada in lista_letras_utilizadas:
        if(letra_utilizada == letra_entrada):
            return 1
    return 0

def imprimir_informacoes_forca(dicio_jogo_da_forca, letra_repetida, num_chances_fixo):
    print(estagios_forca[num_chances_fixo - dicio_jogo_da_forca["num_atual_chances"]])
    imprimir_palavra_censurada(dicio_jogo_da_forca["palavra_censurada"])
    imprimir_letras_utilizadas(dicio_jogo_da_forca["letras_utilizadas"])
    print(f"Dica: {dicio_jogo_da_forca["dica"]}")
    if (letra_repetida):
        print(f"A letra {letra_repetida} foi repetida. Tente novamente.")
    print(f"Tentativas restantes: {dicio_jogo_da_forca["num_atual_chances"]}")

def receber_info_completa(clientSocket):
    mensagem_completa = ""
    pacote = clientSocket.recv(1024).decode('utf-8')
    if not(pacote):
        clientSocket.close()
        sys.exit("Conexão abruptamente encerrada com o servidor. Encerrando o programa.\n")
    
    i = 0
    while True:
        if ("\n") in pacote:
            mensagem = pacote.split("\n")
            mensagem = mensagem[0]
            mensagem_completa += mensagem
            
            if(i):
                imprimir_depuracao("DEPURAÇÃO: A última parte do pacote foi recebida.")
            else:
                imprimir_depuracao(f"DEPURAÇÃO: O pacote foi recebido integralmente.\nPacote: {pacote}")
            return mensagem_completa
        else:
            mensagem_completa += pacote
            imprimir_depuracao(f"DEPURAÇÃO: Uma parte do pacote foi recebida.\nPacote: {pacote}")
            i += 1
        pacote = clientSocket.recv(1024).decode('utf-8')

def enviar_json_receber_info(clientSocket, dicionario):
    texto_json = json.dumps(dicionario) + "\n"
    clientSocket.sendall(texto_json.encode('utf-8'))
    imprimir_depuracao(f"DEPURACAO: Conteúdo enviado.\nConteúdo: {texto_json}")
    return receber_info_completa(clientSocket)

def enviar_json_receber_dicio(clientSocket, dicionario):
    texto_json = json.dumps(dicionario) + "\n"
    clientSocket.sendall(texto_json.encode('utf-8'))
    imprimir_depuracao(f"DEPURACAO: Conteúdo enviado.\nConteúdo: {texto_json}")
    mensagem = receber_info_completa(clientSocket)
    return json.loads(mensagem)

def jogo_da_forca(clientSocket):
    if not(int(enviar_json_receber_info(clientSocket, dicio_comecar_jogo))):
        print("Não foi possível acessar a palavra. Tente novamente.")
        return
    num_chances_fixo = int(enviar_json_receber_info(clientSocket, dicio_num_chances_fixo))
    while True:
        jogo_da_forca = enviar_json_receber_dicio(clientSocket, dicio_jogo_da_forca)

        if(jogo_da_forca["jogador_ganhou"]):
            print(f"Você ganhou! A palavra era: {jogo_da_forca["palavra_censurada"]}!")
            sleep(2)
            break
        elif(jogo_da_forca["jogador_perdeu"]):
            print(estagios_forca[num_chances_fixo])
            print(f"Que pena! Você perdeu! A palavra era: {jogo_da_forca["palavra_censurada"]}.")
            sleep(2)
            break

        letra_repetida = ""
        while True:
            imprimir_informacoes_forca(jogo_da_forca, letra_repetida, num_chances_fixo)
            letra_repetida = ""
            letra_entrada = input("Insira uma letra:\n")
            if (bool_letra_repetida(letra_entrada, jogo_da_forca["letras_utilizadas"])):
                letra_repetida = letra_entrada
                continue

            dicio_tentativa["mensagem"] = letra_entrada
            enviar_json_receber_info(clientSocket, dicio_tentativa)
            break
        
def num_palavras_disponiveis(clientSocket):
    pacote = enviar_json_receber_info(clientSocket, dicio_num_palavras_disponiveis)
    return int(json.loads(pacote))

def determinar_indexador(clientSocket, numero_palavras):
    while True:
        indexador = input(f"Insira um número de 0 a {numero_palavras}.\n")
        try:
            indexador = int(indexador)
        except:
            print("Insira um valor válido.\n")
            continue
        
        if (indexador <= 0):
            indexador *= -1
        indexador %= numero_palavras

        dicio_indexador["mensagem"] = indexador
        print(dicio_indexador)

        if(int(enviar_json_receber_info(clientSocket, dicio_indexador))):
            break
        else:
            print("Opção inválida.\n")

def opcao_usuario():
    while True:
        opcao = input("Para:\na) Escolher uma palavra: insira 1.\nb) Estabelecer conexão: insira 2.\nc) Encerrar o programa: insira 0.\n")
        try:
            opcao = int(opcao)
        except:
            print("Insira um número válido.")
            continue
        if (0 <= opcao <= 2):
            return opcao
        else:
            print("Insira um intervalo válido.")

def estabeler_conexao():
    serverName = "localhost" #input("Insira o IP do servidor.\n")
    serverPort = 63921 #int(input("Insira a porta do servidor.\n"))
    
    try:
        serverPort = int(serverPort)
    except:
        print("A porta inserida é inválida.")
        return 0
    if not(0 <= serverPort <= 65535):
        print("Porta fora do intervalo esperado.")
        return 0
    
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(10)
    
    try:
        clientSocket.connect((serverName, serverPort))
        print("Conexão estabelecida.")
        return clientSocket
    except TimeoutError:
        print("O tempo para estabelecer conexão se expirou.")
    except ConnectionRefusedError:
        print("A conexão foi recusada. Verifique se a porta referenciada está correta.")
    except:
        print("Não foi possível se conectar ao servidor.\nVerifique se o IP e o endereço são válidos.")
    
    clientSocket.close()
    clientSocket = 0
    sleep(2)
    return clientSocket

def main():
    clientSocket = 0
    while True:
        opcao = opcao_usuario()
        if (opcao == 0):
            if (clientSocket):
                enviar_json_receber_info(clientSocket, dicio_encerrar_conexao)
                clientSocket.close()
            print("Encerrando o programa.")
            break
        elif (opcao == 1):
            if (clientSocket):
                numero_palavras = num_palavras_disponiveis(clientSocket)
                determinar_indexador(clientSocket, numero_palavras)
                jogo_da_forca(clientSocket)
            else:
                print("Estabeleca uma conexão antes de iniciar o jogo.")
        elif (opcao == 2):
            if(clientSocket):
                print("Uma conexão já foi estabelecida.")
            else:
                clientSocket = estabeler_conexao()
        else:
            print("Insira uma opção válida.\n")

main()