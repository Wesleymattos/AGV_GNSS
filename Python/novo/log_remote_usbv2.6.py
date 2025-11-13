import serial
import serial.tools.list_ports
import threading
import pyrebase
import time
import os
import re
from queue import Queue

# ==============================
# CONFIGURAÇÃO DO FIREBASE
# ==============================
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

# ==============================
# VARIÁVEIS GLOBAIS
# ==============================
baud_rates = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000, 460800]
ultima_sentenca = {"raw": "", "raw2": "", "raw3": ""}
ultima_precisao = {"rms": "", "lat_err": "", "lon_err": "", "alt_err": ""}
intervalo_envio_ms = 1000
fila_envio = Queue(maxsize=10)
ser1 = None
ser2 = None
ser3 = None
DEBUG = False

# Regex GPGST
gpgst_pattern = r"\$GPGST,(\d+\.\d+),([\d\.]+),[\d\.]+,[\d\.]+,[-+]?\d+\.\d+,([\d\.]+),([\d\.]+),([\d\.]+)\*"

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
    filtros = [
        "GPGGA", "GPRMC", "GNGGA", "GPGSA", "GPGSV",
        "GNRMC", "GNVTG", "GNZDA", "GPVTG", "GPZDA", "GPGST"
    ]
    for i, f in enumerate(filtros, start=1):
        print(f"{i}: Somente {f}")
    print(f"{len(filtros)+1}: Sem filtro (somente NMEA)")
    print(f"{len(filtros)+2}: Sem filtro mesmo (tudo)")

    try:
        idx = int(input("Escolha: "))
        if 1 <= idx <= len(filtros): return filtros[idx - 1]
        elif idx == len(filtros) + 1: return None
        elif idx == len(filtros) + 2: return "ALL"
    except:
        pass
    return None

# ==============================
# LEITURA SERIAL
# ==============================
def leitura_serial(ser, campo, comandos_txt, filtro_nmea):
    global ultima_sentenca, ultima_precisao
    try:
        if comandos_txt:
            time.sleep(1)
            for cmd in comandos_txt:
                try:
                    ser.write(cmd.encode('utf-8') + b'\r\n')
                except: pass
                time.sleep(0.2)

        buffer = ""
        while True:
            try:
                data = ser.read(ser.in_waiting or 1)
                if not data:
                    time.sleep(0.005)
                    continue
                buffer += data.decode(errors='ignore')
            except Exception as e:
                print(f"Erro leitura {campo}: {e}")
                time.sleep(0.05)
                continue

            linhas = buffer.split('\n')
            buffer = linhas[-1]

            for linha in linhas[:-1]:
                linha = linha.strip()
                if not linha:
                    continue

                if filtro_nmea == "ALL":
                    ultima_sentenca[campo] = linha
                elif linha.startswith('$'):
                    if filtro_nmea is None or linha.startswith(f"${filtro_nmea}"):
                        ultima_sentenca[campo] = linha
                    if linha.startswith("$GPGST"):
                        match = re.match(gpgst_pattern, linha)
                        if match:
                            _, rms, lat_err, lon_err, alt_err = match.groups()
                            ultima_precisao.update({
                                "rms": rms, "lat_err": lat_err,
                                "lon_err": lon_err, "alt_err": alt_err
                            })
            time.sleep(0.005)
    except Exception as e:
        print(f"Erro na leitura serial ({campo}): {e}")

# ==============================
# ENVIO FIREBASE
# ==============================
def sincronizar_envio():
    while True:
        try:
            if not fila_envio.empty():
                dados = fila_envio.get()
                try:
                    db.update({
                        "gnss/raw": dados["sentencas"].get("raw", ""),
                        "gnss/raw2": dados["sentencas"].get("raw2", ""),
                        "gnss/raw3": dados["sentencas"].get("raw3", ""),
                        "gnss_precision": dados["precisao"]
                    })
                except Exception as e:
                    print(f"Erro Firebase: {e}")
        except Exception as e:
            print(f"Erro sincronização: {e}")
        time.sleep(0.02)

# ==============================
# AGENDAR ENVIOS
# ==============================
def agendar_envio():
    global ultima_sentenca, ultima_precisao
    while True:
        try:
            if fila_envio.full():
                fila_envio.get_nowait()
            fila_envio.put({
                "sentencas": {
                    "raw": ultima_sentenca["raw"],
                    "raw2": ultima_sentenca["raw2"],
                    "raw3": ultima_sentenca["raw3"]
                },
                "precisao": ultima_precisao.copy()
            })
        except Exception as e:
            print(f"Erro agendamento: {e}")
        time.sleep(intervalo_envio_ms / 1000.0)

# ==============================
# MONITORAR COMANDOS
# ==============================
def monitorar_comandos():
    global ser1, ser2, ser3
    ultimos = ["", "", ""]
    while True:
        try:
            comandos = [
                db.child("receiver").child("comando").get().val(),
                db.child("receiver").child("comando2").get().val(),
                db.child("receiver").child("comando3").get().val()
            ]
            sers = [ser1, ser2, ser3]
            for i in range(3):
                if comandos[i] and comandos[i] != ultimos[i]:
                    print(f"[COMANDO {i+1}] {comandos[i]}")
                    if sers[i]:
                        try:
                            sers[i].write(comandos[i].encode('utf-8') + b'\r\n')
                        except Exception as e:
                            print(f"Falha ao enviar comando{i+1}: {e}")
                    ultimos[i] = comandos[i]
        except Exception as e:
            print(f"Erro monitorar comandos: {e}")
        time.sleep(0.2)

# ==============================
# FUNÇÃO PRINCIPAL
# ==============================
def iniciar_terminal():
    global intervalo_envio_ms, ser1, ser2, ser3

    print("=== Leitura NMEA Tripla com Envio Firebase ===\n")

    portas = listar_portas()
    if len(portas) < 3:
        print("É necessário pelo menos 3 portas USB conectadas.")
        return

    for i, porta in enumerate(portas):
        print(f"{i+1}: {porta}")

    try:
        idxs = [int(input(f"Escolha número da Porta Serial {n+1}: ")) - 1 for n in range(3)]
        if len(set(idxs)) < 3:
            print("As portas devem ser diferentes.")
            return

        portas_sel = [portas[i] for i in idxs]
        bauds = [int(input(f"Baud Rate para Porta {n+1} (ex: 115200): ")) for n in range(3)]
        if not all(b in baud_rates for b in bauds):
            print("Baud inválido.")
            return

        filtro = escolher_filtro_nmea()
        velocidades_ms = [15, 100, 500, 1000, 2000]
        print("\n1: 15ms | 2:100ms | 3:500ms | 4:1000ms | 5:2000ms")
        vel = int(input("Velocidade: "))
        intervalo_envio_ms = velocidades_ms[vel-1] if 1 <= vel <= 5 else 1000

        comandos = carregar_comandos()

        ser1 = serial.Serial(portas_sel[0], bauds[0], timeout=0.1)
        ser2 = serial.Serial(portas_sel[1], bauds[1], timeout=0.1)
        ser3 = serial.Serial(portas_sel[2], bauds[2], timeout=0.1)

        threading.Thread(target=leitura_serial, args=(ser1, "raw", comandos, filtro), daemon=True).start()
        threading.Thread(target=leitura_serial, args=(ser2, "raw2", comandos, filtro), daemon=True).start()
        threading.Thread(target=leitura_serial, args=(ser3, "raw3", comandos, filtro), daemon=True).start()
        threading.Thread(target=sincronizar_envio, daemon=True).start()
        threading.Thread(target=agendar_envio, daemon=True).start()
        threading.Thread(target=monitorar_comandos, daemon=True).start()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Encerrando...")
        for s in [ser1, ser2, ser3]:
            try:
                if s and s.is_open: s.close()
            except: pass
        print("Fechado.")
    except Exception as e:
        print(f"Erro: {e}")

# ==============================
# PONTO DE ENTRADA
# ==============================
if __name__ == "__main__":
    iniciar_terminal()
