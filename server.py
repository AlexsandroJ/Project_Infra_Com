# Importações necessárias
import socket          # Para criar e gerenciar sockets UDP
import os              # Para operações com arquivos (ex: exclusão, nomes)
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE  # Constantes de configuração
from utils import receive_file_chunks, send_file_in_chunks, modify_filename  # Funções auxiliares

def run_server():
    """
    Função principal do servidor UDP.
    Escuta requisições de clientes, recebe arquivos, renomeia-os e os devolve.
    """

    # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Vincula o socket ao endereço IP e porta definidos em config.py
    # A partir de agora, o socket receberá pacotes enviados para esse endereço
    sock.bind((SERVER_HOST, SERVER_PORT))
    
    # Informa no console que o servidor está ativo e pronto para receber conexões
    print(f"[SERVIDOR] Escutando em {SERVER_HOST}:{SERVER_PORT}")

    try:
        # Loop infinito: o servidor permanece ativo até ser interrompido
        while True:
            print("\n[SERVIDOR] Aguardando nome do arquivo...")
            
            # Recebe o primeiro pacote: o nome do arquivo (em UTF-8)
            # recvfrom() retorna os dados e o endereço do cliente que enviou
            data, client_addr = sock.recvfrom(BUFFER_SIZE)
            original_filename = data.decode('utf-8')
            print(f"[SERVIDOR] Recebendo arquivo: '{original_filename}' de {client_addr}")

            # Gera um novo nome para o arquivo (ex: "exemplo.txt" → "exemplo_servidor.txt")
            new_filename = modify_filename(original_filename)
            temp_path = new_filename  # Define caminho de armazenamento temporário

            # Recebe o conteúdo completo do arquivo em chunks e salva em disco
            # A função receive_file_chunks lê pacotes até encontrar o sinal END_SIGNAL
            print("[SERVIDOR] Recebendo dados do arquivo...")
            receive_file_chunks(sock, temp_path, BUFFER_SIZE)

            print(f"[SERVIDOR] Arquivo salvo como: {temp_path}")

            # Envia de volta ao cliente o novo nome do arquivo (para que ele saiba como salvá-lo)
            sock.sendto(new_filename.encode('utf-8'), client_addr)

            # Devolve o arquivo (com novo nome) ao cliente, em blocos de até BUFFER_SIZE bytes
            print("[SERVIDOR] Devolvendo arquivo ao cliente...")
            send_file_in_chunks(sock, temp_path, client_addr, BUFFER_SIZE)

            # Opcional: remove o arquivo armazenado temporariamente no servidor
            # Isso evita acúmulo de arquivos se o servidor rodar por muito tempo
            # os.remove(temp_path)

    except KeyboardInterrupt:
        # Trata interrupção manual (Ctrl+C) para encerrar o servidor graciosamente
        print("\n[SERVIDOR] Encerrado pelo usuário.")
    finally:
        # Garante que o socket seja fechado, mesmo em caso de erro ou interrupção
        sock.close()

# Ponto de entrada do script: executa o servidor se este arquivo for executado diretamente
if __name__ == "__main__":
    run_server()