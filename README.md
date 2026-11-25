# Como executar a aplicação

## Requisitos

- Python 3.12 ou superior.
- Não é necessário instalar bibliotecas adicionais. A aplicação utiliza apenas módulos nativos do Python: `socket`, `json`, `threading`, `time` e `sys`.

Para verificar a versão instalada:

```bash
python --version
```

## Passo a passo

### 1. Organizar os arquivos

Coloque os arquivos `Servidor-Teste.py` e `Cliente-Teste.py` na mesma pasta.

Abra um terminal nessa pasta.

### 2. Iniciar o servidor

Execute o seguinte comando:

```bash
python Servidor-Teste.py
```

Mantenha esse terminal aberto. O servidor exibirá o endereço IP e a porta que deverão ser utilizados pelos clientes.

### 3. Iniciar o cliente

Abra outro terminal na mesma pasta e execute:

```bash
python Cliente-Teste.py
```

**Observação:** no Linux ou macOS, pode ser necessário utilizar `python3` no lugar de `python`.

### 4. Conectar ao servidor

No menu do cliente:

1. Digite o endereço IP informado pelo servidor.
2. Digite a porta informada pelo servidor.
3. Digite `2` para estabelecer a conexão.
4. Aguarde a mensagem **"Conexão estabelecida."**.
5. Digite `1` para iniciar uma partida.

### 5. Jogar

1. Digite um número para selecionar a palavra.
2. Informe uma letra por vez para tentar descobrir a palavra.
3. Ao finalizar a partida, o menu principal será exibido novamente.
4. Digite `1` para iniciar uma nova partida ou `0` para sair.

### 6. Conectar múltiplos clientes

Para permitir que vários clientes joguem simultaneamente, basta repetir o passo 3 em outros terminais ou computadores, utilizando o mesmo endereço IP e a mesma porta do servidor.

## Problemas comuns

| Mensagem | Possível causa | Solução |
|---|---|---|
| `A conexão foi recusada` | O servidor não está em execução. | Verifique se o servidor foi iniciado e mantenha seu terminal aberto. |
| `Address already in use` | Já existe um processo utilizando a porta do servidor. | Encerre a instância anterior do servidor (`Ctrl + C` ou fechando o terminal) antes de iniciar outra. |

