import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
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

# Baud rates comuns
baud_rates = [
    300, 600, 1200, 2400, 4800, 9600, 14400,
    19200, 38400, 57600, 115200, 128000, 256000
]

# Função para listar portas disponíveis
def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

# Função que lê da porta serial e envia ao Firebase
def iniciar_leitura(porta, baud_rate):
    try:
        ser = serial.Serial(porta, baud_rate, timeout=1)
        print(f"Conectado à porta {porta} com {baud_rate} bps")
        while True:
            linha = ser.readline().decode(errors='ignore').strip()
            if linha:
                print(f"Recebido: {linha}")
                db.child("gnss").update({"raw": linha})
    except Exception as e:
        print(f"Erro: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir porta serial:\n{e}")

# Interface gráfica
def iniciar_interface():
    def iniciar_thread():
        porta = combo_porta.get()
        try:
            baud = int(combo_baud.get())
        except:
            messagebox.showerror("Erro", "Velocidade inválida.")
            return
        if not porta:
            messagebox.showwarning("Aviso", "Selecione uma porta serial.")
            return
        btn_iniciar.config(state='disabled')
        threading.Thread(target=iniciar_leitura, args=(porta, baud), daemon=True).start()

    janela = tk.Tk()
    janela.title("NMEA para Firebase")
    janela.geometry("300x200")

    tk.Label(janela, text="Porta Serial:").pack(pady=5)
    combo_porta = ttk.Combobox(janela, values=listar_portas(), state="readonly")
    combo_porta.pack()

    tk.Label(janela, text="Baud Rate:").pack(pady=5)
    combo_baud = ttk.Combobox(janela, values=baud_rates, state="readonly")
    combo_baud.set("9600")
    combo_baud.pack()

    btn_iniciar = tk.Button(janela, text="Iniciar", command=iniciar_thread)
    btn_iniciar.pack(pady=20)

    janela.mainloop()

# Inicia
if __name__ == "__main__":
    iniciar_interface()
