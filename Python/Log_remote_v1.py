import tkinter as tk
from tkinter import filedialog
import time
import threading
import pyrebase

# Configuração do Firebase
config = {
    "apiKey": "AIzaSyAxziLelCdeXbYmmkh9LcvcwkHgXld024M",
    "authDomain": "log--analyzer-web.firebaseapp.com",
    "databaseURL": "https://log--analyzer-web-default-rtdb.firebaseio.com",
    "projectId": "log--analyzer-web",
    "storageBucket": "log--analyzer-web.firebasestorage.app",
    "messagingSenderId": "908592112855",
    "appId": "1:908592112855:web:ae60fc51e47a66390f3c92",
    "measurementId": "G-PEWMF5LTLQ"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Função para selecionar arquivos
def escolher_arquivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Selecione um arquivo .nmea")

# Função que envia linhas para o Firebase com delay
def enviar_linhas_para_firebase(caminho_arquivo, campo_destino):
    with open(caminho_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha:
                print(f"Enviando para {campo_destino}: {linha}")
                db.child("gnss").update({campo_destino: linha})
                time.sleep(0.1)

# Threads separadas para cada arquivo
def executar():
    caminho1 = escolher_arquivo()
    caminho2 = escolher_arquivo()

    t1 = threading.Thread(target=enviar_linhas_para_firebase, args=(caminho1, "raw"))
    t2 = threading.Thread(target=enviar_linhas_para_firebase, args=(caminho2, "raw2"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
    print("Finalizado!")

if __name__ == "__main__":
    executar()
