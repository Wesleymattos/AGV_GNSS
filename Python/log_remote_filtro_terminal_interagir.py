import serial
import serial.tools.list_ports
import threading
import pyrebase
import time
import os

# Configuração do Firebase
config = {
    "apiKey": "AIzaSyAxziLelCdeXbYmmkh9LcvcwkHgXld024M",
    "authDomain": "log--analyzer-web.firebaseapp.com",
    "databaseURL": "https://log--analyzer-web-default-rtdb.firebaseio.com",
    "projectId": "log--analyzer-web",
    "storageBucket": "log--analyzer-web.appspot.com",
    "messagingSenderId": "908592112855",
    "appId": "1:908592112855:web:ae60fc51e47a66390f3c92",
    "measurementId": "G-PEWMF5LTLQ"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

baud_rates = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
ultima_sentenca = {"raw": "", "raw2": ""}
intervalo_envio_ms = 1000  # fixado em 1 segundo

def carregar_comandos():
    caminho = "comando.txt"
    if not os.path.exists(caminho):
        print("Arquivo comando.txt não encontrado.")
        return []
    with open(caminho, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]

def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

def escolher_filtro_nmea():
    print("\nDeseja aplicar filtro NMEA?")
    filtros_disponiveis = ["GPGGA", "GPRMC", "GNGGA", "GPGSA", "GPGSV", "GNRMC", "GNVTG", "GNZDA", "GPVTG", "GPZDA"]
    for i, f in enumerate(filtros_disponiveis, start=1):
        print(f"{i}: Somente {f}")
    print(f"{len(filtros_disponiveis)+1}: Sem filtro (enviar todas as sentenças)")
    opcao = input("Escolha uma opção: ")
    try:
        idx = int(opcao)
        if 1 <= idx <= len(filtros_disponiveis):
            return filtros_disponiveis[idx - 1]
        else:
            return None
    except:
        return None

def leitura_serial(porta, baud, campo, comandos_txt, filtro_nmea):
    global ultima_sentenca
    try:
        ser = serial.Serial(porta, baud, timeout=1)
        print(f"Conectado à {porta} ({baud} bps) – campo '{campo}'")
        if comandos_txt:
            time.sleep(1)
            for cmd in comandos_txt:
                ser.write(cmd.encode('utf-8') + b'\r\n')
                print(f"Comando enviado para {porta}: {cmd}")
                time.sleep(0.2)
        buffer = ""
        while True:
            buffer += ser.read(ser.in_waiting or 1).decode(errors='ignore')
            linhas = buffer.split('\n')
            buffer = linhas[-1]
            for linha in linhas[:-1]:
                linha = linha.strip()
                if linha.startswith('$'):
                    if filtro_nmea is None or linha.startswith(f"${filtro_nmea}"):
                        ultima_sentenca[campo] = linha
            time.sleep(0.05)
    except Exception as e:
        print(f"Erro na porta {porta}: {e}")

def sincronizar_envio():
    global ultima_sentenca, intervalo_envio_ms
    while True:
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        db.child("gnss").update({
            "raw": ultima_sentenca["raw"],
            "raw2": ultima_sentenca["raw2"]
        })
        print(f"[{timestamp}] Enviado para Firebase:")
        print(f"  raw : {ultima_sentenca['raw']}")
        print(f"  raw2: {ultima_sentenca['raw2']}")
        time.sleep(intervalo_envio_ms / 1000.0)

def ler_resposta_multipla(ser, timeout=3.0):
    fim = time.time() + timeout
    resposta = []
    while time.time() < fim:
        if ser.in_waiting:
            dados = ser.read(ser.in_waiting).decode(errors='ignore')
            linhas = dados.splitlines()
            resposta.extend(linhas)
        time.sleep(0.1)
    return '\n'.join(resposta).strip()

def terminal_interativo(ser1, ser2):
    print("\nModo interativo iniciado.")
    print("Digite comandos como:")
    print("  1:log version → envia para Porta 1")
    print("  2:log version → envia para Porta 2")
    print("  ambos:log version → envia para ambas")
    print("  sair → encerra o modo interativo\n")

    while True:
        entrada = input(">> ").strip()
        if entrada.lower() == "sair":
            print("Encerrando modo interativo.")
            break
        try:
            if entrada.startswith("1:"):
                comando = entrada[2:].strip()
                ser1.write((comando + '\r\n').encode())
                print(f"Enviado para Porta 1: {comando}")
                resposta = ler_resposta_multipla(ser1)
                if resposta:
                    print(f"Resposta bruta da Porta 1:\n{resposta}")
                    db.child("gnss").update({"resposta_manual_1": resposta})
            elif entrada.startswith("2:"):
                comando = entrada[2:].strip()
                ser2.write((comando + '\r\n').encode())
                print(f"Enviado para Porta 2: {comando}")
                resposta = ler_resposta_multipla(ser2)
                if resposta:
                    print(f"Resposta bruta da Porta 2:\n{resposta}")
                    db.child("gnss").update({"resposta_manual_2": resposta})
            elif entrada.startswith("ambos:"):
                comando = entrada[6:].strip()
                ser1.write((comando + '\r\n').encode())
                ser2.write((comando + '\r\n').encode())
                print(f"Enviado para ambas as portas: {comando}")
                resposta1 = ler_resposta_multipla(ser1)
                resposta2 = ler_resposta_multipla(ser2)
                if resposta1:
                    print(f"Resposta bruta da Porta 1:\n{resposta1}")
                    db.child("gnss").update({"resposta_manual_1": resposta1})
                if resposta2:
                    print(f"Resposta bruta da Porta 2:\n{resposta2}")
                    db.child("gnss").update({"resposta_manual_2": resposta2})
            else:
                print("Formato inválido. Use '1:', '2:' ou 'ambos:' antes do comando.")
        except Exception as e:
            print(f"Erro ao enviar comando: {e}")

def iniciar_terminal():
    print("=== Leitura NMEA Dupla com Filtro e Envio Sincronizado ===\n")
    portas = listar_portas()
    if not portas:
        print("Nenhuma porta serial encontrada.")
        return
    print("Portas disponíveis:")
    for i, porta in enumerate(portas):
        print(f"{i + 1}: {porta}")
    try:
        idx1 = int(input("Escolha o número da Porta Serial 1: ")) - 1
        idx2 = int(input("Escolha o número da Porta Serial 2: ")) - 1
        if idx1 == idx2:
            print("As portas devem ser diferentes.")
            return
        porta1 = portas[idx1]
        porta2 = portas[idx2]
        baud1 = int(input("Digite o Baud Rate para Porta 1 (ex: 115200): "))
        baud2 = int(input("Digite o Baud Rate para Porta 2 (ex: 115200): "))
        if baud1 not in baud_rates or baud2 not in baud_rates:
            print("Baud rate inválido.")
            return
        filtro = escolher_filtro_nmea()
        comandos = carregar_comandos()

        ser1 = serial.Serial(porta1, baud1, timeout=1)
        ser2 = serial.Serial(porta2, baud2, timeout=1)

        threading.Thread(target=leitura_serial, args=(porta1, baud1, "raw", comandos, filtro), daemon=True).start()
        threading.Thread(target=leitura_serial, args=(porta2, baud2, "raw2", comandos, filtro), daemon=True).start()
        threading.Thread(target=sincronizar_envio, daemon=True).start()
        threading.Thread(target=terminal_interativo, args=(ser1, ser2), daemon=True).start()

        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    iniciar_terminal()
