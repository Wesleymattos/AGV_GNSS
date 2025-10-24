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

baud_rates = [
    300, 600, 1200, 2400, 4800, 9600, 14400,
    19200, 38400, 57600, 115200, 128000, 256000
]

def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

def iniciar_leitura(porta, baud, campo):
    try:
        ser = serial.Serial(porta, baud, timeout=1)
        print(f"Conectado à {porta} ({baud} bps) → campo '{campo}'")
        while True:
            linha = ser.readline().decode(errors='ignore').strip()
            if linha:
                print(f"[{campo}] {linha}")
                db.child("gnss").update({campo: linha})
    except Exception as e:
        print(f"Erro na porta {porta}: {e}")
        messagebox.showerror("Erro", f"Erro na porta {porta}:\n{e}")

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

        btn_iniciar.config(state='disabled')
        threading.Thread(target=iniciar_leitura, args=(p1, b1, "raw"), daemon=True).start()
        threading.Thread(target=iniciar_leitura, args=(p2, b2, "raw2"), daemon=True).start()

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
    combo_baud1.set("9600")
    combo_baud1.pack()

    # Porta 2
    tk.Label(janela, text="Porta Serial 2:").pack(pady=(10, 0))
    combo_porta2 = ttk.Combobox(janela, values=portas, state="readonly")
    combo_porta2.pack()

    tk.Label(janela, text="Baud Rate 2:").pack()
    combo_baud2 = ttk.Combobox(janela, values=baud_rates, state="readonly")
    combo_baud2.set("9600")
    combo_baud2.pack()

    # Botão iniciar
    btn_iniciar = tk.Button(janela, text="Iniciar Leitura", command=iniciar_thread)
    btn_iniciar.pack(pady=20)

    janela.mainloop()

if __name__ == "__main__":
    iniciar_interface()
