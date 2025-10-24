import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import pyrebase
import time
import os
import socket

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

baud_rates = [
    300, 600, 1200, 2400, 4800, 9600, 14400,
    19200, 38400, 57600, 115200, 128000, 256000
]

ARQUIVO_COMANDO = "comando.txt"

def internet_disponivel():
    """Testa conexão com a internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def carregar_comandos():
    """Lê o comando.txt e retorna lista de comandos."""
    if not os.path.exists(ARQUIVO_COMANDO):
        print("Arquivo comando.txt não encontrado.")
        return []
    with open(ARQUIVO_COMANDO, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]

def listar_portas():
    """Lista portas seriais disponíveis."""
    return [port.device for port in serial.tools.list_ports.comports()]

def iniciar_leitura(porta, baud, campo, comandos_txt):
    """Loop eterno de reconexão e leitura/envio."""
    while True:
        try:
            # Espera internet voltar
            while not internet_disponivel():
                print(f"[{campo}] Aguardando internet voltar...")
                time.sleep(2)

            # Tenta abrir a porta serial até conseguir
            while True:
                try:
                    ser = serial.Serial(porta, baud, timeout=1)
                    print(f"[{campo}] Conectado à {porta} ({baud} bps)")
                    break
                except serial.SerialException:
                    print(f"[{campo}] Porta {porta} não encontrada, tentando novamente...")
                    time.sleep(2)

            # Envia comandos iniciais
            if comandos_txt:
                time.sleep(1)
                for cmd in comandos_txt:
                    ser.write(cmd.encode('utf-8') + b'\r\n')
                    print(f"[{campo}] Comando enviado: {cmd}")
                    time.sleep(0.2)

            # Loop de leitura contínuo
            while True:
                if not internet_disponivel():
                    print(f"[{campo}] Internet caiu! Aguardando reconexão...")
                    ser.close()
                    break  # Sai para reiniciar o ciclo

                try:
                    linha = ser.readline().decode(errors='ignore').strip()
                except serial.SerialException:
                    print(f"[{campo}] Porta {porta} desconectada!")
                    break  # Sai para tentar reconectar

                if linha:
                    partes = linha.split('$')
                    for parte in partes:
                        parte = parte.strip()
                        if parte:
                            sentenca = '$' + parte
                            print(f"[{campo}] {sentenca}")
                            try:
                                db.child("gnss").update({campo: sentenca})
                            except Exception as e:
                                print(f"[{campo}] Erro ao enviar ao Firebase: {e}")
                                break  # Sai para reconectar internet

        except Exception as e:
            print(f"[{campo}] Erro geral: {e}")
            time.sleep(2)

def iniciar_interface():
    def iniciar_thread():
        p1 = combo_porta1.get()
        p2 = combo_porta2.get()
        try:
            b1 = int(combo_baud1.get())
            b2 = int(combo_baud2.get())
        except:
            messagebox.showerror("Erro", "Baud inválido.")
            return
        if not p1 or not p2:
            messagebox.showwarning("Aviso", "Selecione ambas as portas.")
            return
        if p1 == p2:
            messagebox.showerror("Erro", "As portas devem ser diferentes.")
            return

        comandos = carregar_comandos()

        btn_iniciar.config(state='disabled')
        threading.Thread(target=iniciar_leitura, args=(p1, b1, "raw", comandos), daemon=True).start()
        threading.Thread(target=iniciar_leitura, args=(p2, b2, "raw2", comandos), daemon=True).start()

    janela = tk.Tk()
    janela.title("Leitura NMEA Dupla para Firebase")
    janela.geometry("400x300")

    portas = listar_portas()

    # Porta 1
    tk.Label(janela, text="Porta Serial 1:").pack()
    combo_porta1 = ttk.Combobox(janela, values=portas, state="readonly")
    combo_porta1.pack()

    tk.Label(janela, text="Baud Rate 1:").pack()
    combo_baud1 = ttk.Combobox(janela, values=baud_rates, state="readonly")
    combo_baud1.set("115200")
    combo_baud1.pack()

    # Porta 2
    tk.Label(janela, text="Porta Serial 2:").pack(pady=(10, 0))
    combo_porta2 = ttk.Combobox(janela, values=portas, state="readonly")
    combo_porta2.pack()

    tk.Label(janela, text="Baud Rate 2:").pack()
    combo_baud2 = ttk.Combobox(janela, values=baud_rates, state="readonly")
    combo_baud2.set("115200")
    combo_baud2.pack()

    # Botão iniciar
    btn_iniciar = tk.Button(janela, text="Iniciar Leitura e Enviar Comandos", command=iniciar_thread)
    btn_iniciar.pack(pady=20)

    janela.mainloop()

if __name__ == "__main__":
    iniciar_interface()
