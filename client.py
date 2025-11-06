# client.py

# Importação das bibliotecas necessárias
import socket          # Para comunicação via sockets (rede)
import sys             # Para acessar argumentos da linha de comando
import os              # Para operações com sistema de arquivos (ex: verificar existência de arquivo)
import logging         # Para registrar mensagens de log (substitui print de forma controlada)

# Importação de constantes e funções auxiliares do projeto
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
from utils import send_file_in_chunks, receive_file_chunks

# Configura o nível básico do logging para exibir mensagens de nível INFO e superiores
# Isso permite que logs como logging.info() e logging.error() sejam exibidos no console
logging.basicConfig(level=logging.INFO)

def run_client(filepath):
    """
    Função principal do cliente UDP.
    Envia um arquivo para o servidor, recebe de volta com nome modificado e salva localmente.
    
    Parâmetros:
        filepath (str): Caminho absoluto ou relativo do arquivo a ser enviado.
    """
    
    # Verifica se o arquivo existe no sistema de arquivos
    if not os.path.isfile(filepath):
        # Se não existir, registra um erro e encerra a função
        logging.error(f"Arquivo não encontrado: {filepath}")
        return  # Sai da função sem tentar enviar

    # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Define o endereço do servidor (IP e porta) para onde os dados serão enviados
    server_addr = (SERVER_HOST, SERVER_PORT)

    try:
        # Extrai apenas o nome do arquivo (sem o caminho completo)
        filename = os.path.basename(filepath)
        
        # Envia o nome do arquivo como primeiro pacote (em UTF-8)
        sock.sendto(filename.encode('utf-8'), server_addr)
        logging.info(f"[CLIENTE] Enviando arquivo: {filename}")

        # Envia o conteúdo do arquivo em blocos de até BUFFER_SIZE bytes
        # A função send_file_in_chunks lida com a leitura e envio em chunks
        send_file_in_chunks(sock, filepath, server_addr, BUFFER_SIZE)

        # Recebe do servidor o novo nome do arquivo (com sufixo "_servidor")
        # recvfrom() retorna os dados e o endereço do remetente (ignorado aqui com _)
        data, _ = sock.recvfrom(BUFFER_SIZE)
        new_filename = data.decode('utf-8')  # Decodifica de bytes para string
        
        # Define o caminho onde o arquivo devolvido será salvo localmente
        output_path = f"received_{new_filename}"
        logging.info(f"[CLIENTE] Recebendo arquivo de volta como: {new_filename}")

        # Recebe o conteúdo do arquivo devolvido pelo servidor e salva em disco
        receive_file_chunks(sock, output_path, BUFFER_SIZE)
        logging.info(f"[CLIENTE] Arquivo salvo localmente como: {output_path}")

    except Exception as e:
        # Captura qualquer exceção (ex: timeout, erro de rede, etc.) e registra
        logging.error(f"[ERRO] {e}")
    finally:
        # Garante que o socket seja fechado, mesmo em caso de erro
        sock.close()

# Ponto de entrada do script (executado apenas se este arquivo for chamado diretamente)
if __name__ == "__main__":
    # Verifica se foi passado exatamente um argumento (o caminho do arquivo)
    if len(sys.argv) != 2:
        # Se não, exibe mensagem de uso e encerra com código de erro
        logging.info("Uso: python client.py <caminho_do_arquivo>")
        sys.exit(1)  # Código 1 indica erro de uso

    # Chama a função principal com o caminho fornecido pelo usuário
    run_client(sys.argv[1])