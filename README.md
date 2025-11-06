# 📤 Transferência de Arquivos via UDP em Python

Este projeto implementa um sistema simples de **envio e devolução de arquivos** usando o protocolo **UDP** (User Datagram Protocol) com a biblioteca `socket` do Python. O cliente envia um arquivo ao servidor, que o armazena com um novo nome e o devolve ao cliente. A comunicação é feita em **pacotes de até 1024 bytes**, conforme exigido.

> ✅ **Etapa 1**: Implementação básica sem confiabilidade (sem ACKs, retransmissões ou correção de erros).  
> 🔜 **Etapa 2 (futura)**: Adição de mecanismos de entrega confiável.

## 📁 Estrutura do Projeto
```
PROJECT_INFRA_COM/
├── config.py
├── utils.py
├── server.py
├── client.py
└── tests/
```

## 🚀 Como Usar

### Pré-requisitos
- Python 3.6 ou superior
- Nenhuma dependência externa (apenas bibliotecas padrão do Python)

### Rodar Testes
Abra um terminal na raiz do projeto e execute:
```
python -m unittest tests.test_transfer -v
```

### Iniciar o Servidor
Abra um terminal e execute:
```
python server.py
```
