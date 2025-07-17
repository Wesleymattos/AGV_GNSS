import time
import tkinter as tk
from tkinter import filedialog
import firebase_admin
from firebase_admin import credentials, db

# Caminho para o arquivo JSON da sua conta de serviço Firebase
CAMINHO_CRED = 'credenciais.json'  # substitua pelo caminho real

# Inicializa o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(CAMINHO_CRED)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://SEU_PROJETO.firebaseio.com/'  # substitua pela URL do seu projeto
    })

def enviar_para_firebase(nó, linha):
    try:
        ref = db.reference(nó)
        ref.set(linha)
        print(f"Enviado para {nó}: {linha}")
    except Exception as e:
        print(f"Erro ao enviar para o Firebase: {e}")

def processar_arquivo(file_path, no_firebase):
    print(f"Lendo {file_path} e enviando para nó '{no_firebase}'...")
    with open(file_path, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                enviar_para_firebase(no_firebase, linha)
                time.sleep(2)

# Abre janela para selecionar 2 arquivos
root = tk.Tk()
root.withdraw()

file_paths = filedialog.askopenfilenames(
    title="Selecione exatamente dois arquivos .txt",
    filetypes=[("Text files", "*.txt"), ("Todos os arquivos", "*.*")]
)

# Garante que dois arquivos foram selecionados
if len(file_paths) != 2:
    print("Erro: selecione exatamente dois arquivos.")
else:
    processar_arquivo(file_paths[0], "raw")
    processar_arquivo(file_paths[1], "raw2")
