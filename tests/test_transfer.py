# test_transfer.py

# Importações necessárias para testes automatizados
import unittest          # Framework de testes nativo do Python
import os                # Para operações com arquivos e diretórios
import tempfile          # Para criar arquivos/diretórios temporários de forma segura
import subprocess        # Para executar o servidor como um processo externo
import time              # Para dar tempo ao servidor de inicializar
import hashlib           # Para verificar a integridade dos arquivos via hash

# Importa a função principal do cliente e utilitários do projeto

from client import run_client
from utils import modify_filename

# === CONFIGURAÇÕES DOS TESTES ===

# Nome do script do servidor a ser executado durante os testes
SERVER_SCRIPT = "server.py"

# Dicionário com arquivos de teste: nome do arquivo -> conteúdo binário
# Cobre casos comuns: texto, vazio, binário, imagem simulada
TEST_FILES = {
    "small.txt": b"Hello, UDP!",               # Arquivo de texto pequeno
    "empty.txt": b"",                          # Arquivo vazio (caso limite)
    "medium.jpg": b"\xFF\xD8\xFF\xE0" + b"\x00" * 2000,  # Cabeçalho JPEG + dados
    "binary.bin": bytes(range(256)) * 10,      # Bytes de 0 a 255 repetidos 10 vezes (2560 bytes)
}


# === CLASSE DE TESTES ===
class TestUDPFileTransfer(unittest.TestCase):
    """
    Conjunto de testes automatizados para o sistema de transferência de arquivos UDP.
    Inclui inicialização/encerramento automático do servidor e validação de integridade.
    """

    @classmethod
    def setUpClass(cls):
        """
        Método executado UMA VEZ antes de todos os testes da classe.
        Inicia o servidor UDP em um processo separado para que os testes possam se comunicar com ele.
        """
        cls.server_process = subprocess.Popen(
            ["python", SERVER_SCRIPT],           # Comando para executar o servidor
            stdout=subprocess.DEVNULL,           # Suprime saída padrão do servidor
            stderr=subprocess.DEVNULL            # Suprime erros do servidor (opcional em produção)
        )
        time.sleep(1)  # Aguarda 1 segundo para garantir que o socket do servidor esteja pronto

    @classmethod
    def tearDownClass(cls):
        """
        Método executado UMA VEZ após todos os testes.
        Encerra o processo do servidor para liberar a porta e recursos.
        """
        cls.server_process.terminate()  # Envia sinal de término
        cls.server_process.wait()       # Aguarda o processo encerrar de fato

    def compute_hash(self, filepath):
        """
        Calcula o hash SHA-256 de um arquivo.
        Usado para verificar se o arquivo recebido é **bit a bit igual** ao original.
        
        Parâmetros:
            filepath (str): Caminho do arquivo a ser verificado.
        
        Retorna:
            str: Hash SHA-256 em formato hexadecimal.
        """
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def test_file_transfer(self):
        """
        Teste principal: envia vários tipos de arquivos e valida:
        - Se o arquivo foi recebido,
        - Se o nome foi alterado corretamente,
        - Se o conteúdo é idêntico ao original (via hash).
        """
        # Itera sobre cada arquivo de teste
        for filename, content in TEST_FILES.items():
            # Usa subTest para isolar falhas (permite que um falhe sem interromper os outros)
            with self.subTest(filename=filename):
                # Cria um diretório temporário que será automaticamente apagado após o bloco
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Caminho completo para o arquivo original de teste
                    original_path = os.path.join(tmpdir, filename)
                    
                    # Escreve o conteúdo binário no arquivo temporário
                    with open(original_path, "wb") as f:
                        f.write(content)

                    # Calcula hash do arquivo original para comparação futura
                    original_hash = self.compute_hash(original_path)

                    # Executa o cliente, que envia o arquivo e recebe de volta
                    run_client(original_path)

                    # Determina o nome esperado do arquivo recebido
                    expected_new_name = modify_filename(filename)  # ex: "small.txt" → "small_servidor.txt"
                    received_path = os.path.join(os.getcwd(), f"received_{expected_new_name}")

                    # Verifica se o arquivo devolvido foi realmente criado
                    self.assertTrue(
                        os.path.exists(received_path),
                        f"Arquivo recebido não encontrado: {received_path}"
                    )

                    # Compara os hashes para garantir integridade binária
                    received_hash = self.compute_hash(received_path)
                    self.assertEqual(
                        original_hash, received_hash,
                        f"Hash incompatível para {filename} (arquivo corrompido ou incompleto)"
                    )

                    # Remove o arquivo recebido para não poluir o diretório entre testes
                    os.remove(received_path)

    def test_nonexistent_file(self):
        """
        Testa o comportamento do cliente ao tentar enviar um arquivo que não existe.
        Verifica se uma mensagem de erro apropriada é registrada via logging.
        """
        # Captura todas as mensagens de log geradas durante a chamada
        with self.assertLogs() as cm:
            run_client("arquivo_inexistente.xyz")
        
        # Verifica se alguma das mensagens de log contém a frase esperada
        self.assertTrue(
            any("Arquivo não encontrado" in msg for msg in cm.output),
            "Mensagem de erro esperada não foi registrada no log"
        )


# === PONTO DE ENTRADA PARA EXECUÇÃO DOS TESTES ===
if __name__ == "__main__":
    # Executa todos os testes com nível de detalhe 2 (mostra nome de cada subteste)
    unittest.main(verbosity=2)