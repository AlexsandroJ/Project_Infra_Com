# utils.py

# Importações
import os                     # Para manipulação de caminhos e nomes de arquivos
from config import END_SIGNAL  # Sinalizador de fim de transmissão (definido em config.py)

def send_file_in_chunks(sock, filepath, target_addr, chunk_size=1024):
    """
    Envia um arquivo em blocos (chunks) via socket UDP.
    
    Esta função lê o arquivo em modo binário e envia cada trecho de até `chunk_size` bytes
    para o endereço de destino. Ao finalizar, envia um sinal especial (`END_SIGNAL`)
    para indicar que a transmissão do arquivo terminou.

    Parâmetros:
        sock (socket.socket): Socket UDP já criado.
        filepath (str): Caminho do arquivo a ser enviado.
        target_addr (tuple): Tupla (IP, porta) do destinatário.
        chunk_size (int): Tamanho máximo de cada pacote (padrão: 1024 bytes).
    """
    # Abre o arquivo em modo binário para leitura
    with open(filepath, "rb") as f:
        while True:
            # Lê um bloco de até `chunk_size` bytes
            chunk = f.read(chunk_size)
            # Se não houver mais dados (fim do arquivo), sai do loop
            if not chunk:
                break
            # Envia o bloco para o destinatário
            sock.sendto(chunk, target_addr)
    
    # Após enviar todo o conteúdo, envia o sinalizador de fim de transmissão
    sock.sendto(END_SIGNAL, target_addr)


def receive_file_chunks(sock, output_path, chunk_size=1024):
    """
    Recebe um arquivo em blocos via socket UDP e salva em disco.
    
    A função fica em loop recebendo pacotes até encontrar o `END_SIGNAL`.
    Todos os dados recebidos (exceto o sinal de fim) são escritos no arquivo de saída.

    Parâmetros:
        sock (socket.socket): Socket UDP já vinculado (em uso).
        output_path (str): Caminho onde o arquivo recebido será salvo.
        chunk_size (int): Tamanho máximo esperado por pacote (deve ser ≥ BUFFER_SIZE).

    Retorna:
        tuple: Endereço (IP, porta) do último remetente (útil para respostas em servidor).
    """
    # Abre (ou cria) o arquivo de destino em modo binário para escrita
    with open(output_path, "wb") as f:
        while True:
            # Recebe um pacote de até `chunk_size` bytes
            data, addr = sock.recvfrom(chunk_size)
            
            # Verifica se o pacote recebido é o sinal de fim de transmissão
            if data == END_SIGNAL:
                break  # Sai do loop: arquivo completo recebido
            
            # Escreve os dados recebidos no arquivo
            f.write(data)
    
    # Retorna o endereço do cliente (útil no servidor para saber para quem responder)
    return addr


def modify_filename(filename):
    """
    Modifica o nome de um arquivo adicionando o sufixo '_servidor' antes da extensão.
    
    Exemplos:
        "foto.jpg"    → "foto_servidor.jpg"
        "dados.txt"   → "dados_servidor.txt"
        "arquivo"     → "arquivo_servidor"  (sem extensão)

    Parâmetros:
        filename (str): Nome original do arquivo.

    Retorna:
        str: Novo nome do arquivo com sufixo inserido.
    """
    # Separa o nome base da extensão (ex: "documento.pdf" → ("documento", ".pdf"))
    base, ext = os.path.splitext(filename)
    # Reconstrói com o sufixo antes da extensão
    return f"{base}_servidor{ext}"