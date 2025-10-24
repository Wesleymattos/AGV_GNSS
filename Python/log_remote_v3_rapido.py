import tkinter as tk
from tkinter import filedialog
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

# Função que lê 10 linhas por vez e envia cada uma separadamente
def enviar_sentencas_individuais(caminho_arquivo, campo_destino):
    buffer = []
    with open(caminho_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha:
                buffer.append(linha)
                if len(buffer) == 2:
                    for sentenca in buffer:
                        print(f"Enviando para {campo_destino}: {sentenca}")
                        db.child("gnss").update({campo_destino: sentenca})
                    buffer = []
        # Envia o restante se houver menos de 5 no final
        if buffer:
            for sentenca in buffer:
                print(f"Enviando última sentença para {campo_destino}: {sentenca}")
                db.child("gnss").update({campo_destino: sentenca})

# Função principal com threads
def executar():
    caminho1 = escolher_arquivo()
    caminho2 = escolher_arquivo()

    t1 = threading.Thread(target=enviar_sentencas_individuais, args=(caminho1, "raw"))
    t2 = threading.Thread(target=enviar_sentencas_individuais, args=(caminho2, "raw2"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
    print("Finalizado!")

if __name__ == "__main__":
    executar()
