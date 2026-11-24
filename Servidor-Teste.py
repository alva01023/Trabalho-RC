import socket
import json
import threading

NUM_CHANCES_FIXO = 7
NUM_REVELAR_DICA = 3
MODO_DEPURACAO = 1

lista_palavras = ["a"*2500,
                  "pneumoultramicroscopicossilicovulcanoconiotico",
                  "helicoptero",
                  "impressora",
                  "distinguir",
                  "cumprir",
                  "sereno",
                  "rubi",
                  "anil",
                  "podio",
                  "roxo"]

lista_dicas = ["Depuracao",
               "Maior palavra da nossa lingua.",
               "Meio de transporte.",
               "Eletronico comum em empresas.",
               "Verbo. Sinonimo de diferenciar.",
               "Verbo. Sinonimo de honrar.",
               "Sinonimo de tranquilo.",
               "Cristal vermelho.",
               "Cor presente no arco-iris.",
               "Plataforma onde vencedores sobem.",
               "Uma cor."]

def imprimir_depuracao(mensagem):
    if (MODO_DEPURACAO):
        print(mensagem)
        
def verificar_jogador_ganhou(palavra_censurada):
    imprimir_depuracao("DEPURAÇÃO: Função executada: verificar_jogador_ganhou")
    for letra in palavra_censurada:
        if (letra == "_"):
            return 0
    return 1

def verificar_jogador_acertou(letra_tentativa, palavra_escolhida):
    imprimir_depuracao("DEPURAÇÃO: Função executada: verificar_jogador_acertou")
    for letra in palavra_escolhida:
        if (letra == letra_tentativa):
            return 1
    return 0

def atualizar_palavra_censurada(letra_tentativa, palavra_censurada, palavra_escolhida):
    imprimir_depuracao("DEPURAÇÃO: Função executada: atualizar_palavra_censurada")
    i = 0
    palavra_censurada_atualizada = []
    for letra in palavra_censurada:
        if(letra_tentativa == palavra_escolhida[i]):
            letra = letra_tentativa   
        palavra_censurada_atualizada.append(letra)
        i += 1
    palavra_censurada_atualizada = "".join(palavra_censurada_atualizada)
    return palavra_censurada_atualizada

def verificar_letra_repetida(letra, letras_utilizadas):
    imprimir_depuracao("DEPURAÇÃO: Função executada: verificar_letra_repetida")
    for letra_utilizada in letras_utilizadas:
        if (letra == letra_utilizada):
            return 1
    return 0

def verificar_entrada_valida(letra_tentativa):
    imprimir_depuracao("DEPURAÇÃO: Função executada: verificar_entrada_valida")
    try:
        letra_tentativa = letra_tentativa[0].lower()
    except:
        return 0

    if not("a" <= letra_tentativa <= "z"):
        return 0
    return letra_tentativa

def enviar_cliente(socket_conexao, conteudo):
    conteudo += "\n"
    imprimir_depuracao(f"DEPURAÇÃO: Função executada: enviar_cliente. Argumento: \n   - {conteudo}")
    socket_conexao.sendall(conteudo.encode('utf-8'))    

def pacote_indexador(socket_conexao, mensagem):
    """bool cliente e int servidor"""
    imprimir_depuracao("DEPURAÇÃO: Tratando pacote do tipo indexador.")

    try:
        indexador = int(mensagem)
    except:
        enviar_cliente(socket_conexao, "0")
        return -1

    if(indexador <= 0):
        indexador *= -1
    indexador %= len(lista_palavras)

    enviar_cliente(socket_conexao, "1")
    return indexador

def pacote_num_palavras(socket_conexao):
    imprimir_depuracao("DEPURAÇÃO: Tratando pacote do tipo num_palavras.")
    enviar_cliente(socket_conexao, f"{len(lista_palavras)}")

def pacote_num_chances_fixo(socket_conexao):
    imprimir_depuracao("DEPURAÇÃO: Tratando pacote do tipo num_chances_fixo.")
    enviar_cliente(socket_conexao, f"{NUM_CHANCES_FIXO}")

def pacote_comecar_jogo(socket_conexao, palavra_escolhida):
    imprimir_depuracao("DEPURAÇÃO: Tratando pacote do tipo comecar_jogo.")
    if (len(palavra_escolhida)):
        dicio_jogo_atual = {
            "num_atual_chances": NUM_CHANCES_FIXO,
            "palavra_censurada": len(palavra_escolhida)*"_",
            "letras_utilizadas": [],
            "dica": f"A dica será revelada quando {NUM_REVELAR_DICA} tentativas sobrarem.",
            "jogador_perdeu": 0,
            "jogador_ganhou": 0
        }
        enviar_cliente(socket_conexao, "1")
        return dicio_jogo_atual 
    else:
        enviar_cliente(socket_conexao, "0")

def pacote_jogo_da_forca(socket_conexao, dicio_jogo_atual):
    texto_json = json.dumps(dicio_jogo_atual)
    enviar_cliente(socket_conexao, texto_json)

def pacote_tentativa(socket_conexao, dicio_jogo_atual, mensagem, indexador):
    imprimir_depuracao("DEPURAÇÃO: Tratando pacote do tipo tentativa.")
    letra_tentativa = verificar_entrada_valida(mensagem)

    if(letra_tentativa == 0):
        enviar_cliente(socket_conexao, "0")
        return dicio_jogo_atual

    palavra_escolhida = lista_palavras[indexador]
        
    if(verificar_letra_repetida(letra_tentativa, dicio_jogo_atual["letras_utilizadas"])):
        enviar_cliente(socket_conexao, "0")
        return dicio_jogo_atual

    dicio_jogo_atual["letras_utilizadas"].append(letra_tentativa)
    
    if(verificar_jogador_acertou(letra_tentativa, palavra_escolhida)):
        palavra_censurada = dicio_jogo_atual["palavra_censurada"]
        palavra_censurada = atualizar_palavra_censurada(letra_tentativa, palavra_censurada, palavra_escolhida)
        dicio_jogo_atual["palavra_censurada"] = palavra_censurada
        if(verificar_jogador_ganhou(palavra_censurada)):
            dicio_jogo_atual["jogador_ganhou"] = 1
    else:
        dicio_jogo_atual["num_atual_chances"] -= 1
        num_atual_chances = dicio_jogo_atual["num_atual_chances"]
        if(num_atual_chances == NUM_REVELAR_DICA):
            dicio_jogo_atual["dica"] = lista_dicas[indexador]
        if (num_atual_chances <= 0):
            dicio_jogo_atual["jogador_perdeu"] = 1
            dicio_jogo_atual["palavra_censurada"] = palavra_escolhida
    enviar_cliente(socket_conexao, "1")
    return dicio_jogo_atual

def chamada_ou_pacote_encerrar_conexao(socket_conexao):
    imprimir_depuracao("DEPURAÇÃO: Tratando pacote do tipo encerrar_conexao.")
    raddr = socket_conexao.getpeername()
    enviar_cliente(socket_conexao, "1")
    socket_conexao.close()
    imprimir_depuracao(f"Conexão encerrada com {raddr}.")

def receber_info_completa(socket_conexao):
    mensagem_completa = ""
    while True:
        try:
            pacote = socket_conexao.recv(1024).decode('utf-8')
        except:
            pacote = ""

        if not(pacote):
            return pacote
        
        if ("\n") in pacote:
            mensagem = pacote.split("\n")
            mensagem = mensagem[0]
            mensagem_completa += mensagem
            return mensagem_completa
        else:
            mensagem_completa += pacote

def gerenciar_jogo_da_forca(socket_conexao):
    socket_conexao.settimeout(120)
    indexador = -1
    dicio_jogo_atual = 0
    raddr = socket_conexao.getpeername()
    while True:
        imprimir_depuracao("DEPURAÇÃO: Aguardando pacote.")
        pacote = receber_info_completa(socket_conexao)
        if not (pacote):
            imprimir_depuracao(f"DEPURAÇÃO: Pacote vazio recebido. Encerrando conexão com {raddr}.")
            socket_conexao.close()
            break

        try:
            dicio_dados = json.loads(pacote)
        except:
            enviar_cliente(socket_conexao, "-1")
            continue
        
        imprimir_depuracao(f"DEPURAÇÃO: Pacote recebido: {dicio_dados}.")
        tipo_pacote = dicio_dados.get("tipo")

        if(tipo_pacote == "indexador"):
            indexador = pacote_indexador(socket_conexao, dicio_dados.get("mensagem"))
            
        elif(tipo_pacote == "num_palavras"):
            pacote_num_palavras(socket_conexao)

        elif(tipo_pacote == "num_chances_fixo"):
            pacote_num_chances_fixo(socket_conexao)

        elif(tipo_pacote == "comecar_jogo"):
            if (indexador != -1):
                dicio_jogo_atual = pacote_comecar_jogo(socket_conexao, lista_palavras[indexador])
            else:
                enviar_cliente(socket_conexao, "-1")

        elif(tipo_pacote == "jogo_da_forca"):
            if (dicio_jogo_atual):
                pacote_jogo_da_forca(socket_conexao, dicio_jogo_atual)
            else:
                enviar_cliente(socket_conexao, "{}")
            
        elif(tipo_pacote == "tentativa"):
            if (dicio_jogo_atual):
                dicio_jogo_atual = pacote_tentativa(socket_conexao, dicio_jogo_atual, dicio_dados.get("mensagem"), indexador)
            else:
                enviar_cliente(socket_conexao, "-1")

        elif(tipo_pacote == "encerrar_conexao"):
            chamada_ou_pacote_encerrar_conexao(socket_conexao)
            break
        else:
            print("Pacote inválido.")
            enviar_cliente(socket_conexao, "-1")

def main():
    porta_servidor = 59800
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_servidor.bind(('', porta_servidor))
    socket_servidor.listen(1)
    while True:
        print("Aguardando conexão.")
        socket_conexao, addr = socket_servidor.accept()
        print(f"Conexão iniciada com {addr}.")
        conexao_cliente = threading.Thread(target=gerenciar_jogo_da_forca, args=(socket_conexao,), daemon=True)
        conexao_cliente.start()

main()