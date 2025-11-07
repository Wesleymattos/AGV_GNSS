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
ultima_sentenca = {"raw": "", "raw2": ""}
ultima_precisao = {"rms": "", "lat_err": "", "lon_err": "", "alt_err": ""}
intervalo_envio_ms = 1000
fila_envio = Queue(maxsize=10)
ser1 = None
ser2 = None
DEBUG = False

# Regex para capturar GPGST (precisão)
gpgst_pattern = r"\$GPGST,(\d+\.\d+),([\d\.]+),[\d\.]+,[\d\.]+,[-+]?\d+\.\d+,([\d\.]+),([\d\.]+),([\d\.]+)\*"

# ==============================
# FUNÇÕES DE ARQUIVO E PORTA
# ==============================
def carregar_comandos():
    caminho = "comando.txt"
    if not os.path.exists(caminho):
        print("Arquivo comando.txt não encontrado.")
        return []
    with open(caminho, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]

def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

# ==============================
# FUNÇÃO DE FILTRO
# ==============================
def escolher_filtro_nmea():
    print("\nDeseja aplicar filtro NMEA?")
    filtros_disponiveis = [
        "GPGGA", "GPRMC", "GNGGA", "GPGSA", "GPGSV",
        "GNRMC", "GNVTG", "GNZDA", "GPVTG", "GPZDA", "GPGST"
    ]
    for i, f in enumerate(filtros_disponiveis, start=1):
        print(f"{i}: Somente {f}")
    print(f"{len(filtros_disponiveis)+1}: Sem filtro (enviar apenas sentenças NMEA)")
    print(f"{len(filtros_disponiveis)+2}: Sem filtro mesmo (qualquer dado recebido)")

    opcao = input("Escolha uma opção: ")
    try:
        idx = int(opcao)
        if 1 <= idx <= len(filtros_disponiveis):
            return filtros_disponiveis[idx - 1]
        elif idx == len(filtros_disponiveis) + 1:
            return None
        elif idx == len(filtros_disponiveis) + 2:
            return "ALL"
        else:
            return None
    except:
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
                    if DEBUG:
                        print(f"Comando enviado: {cmd}")
                except Exception as e:
                    print(f"Erro ao enviar comando inicial para {campo}: {e}")
                time.sleep(0.2)

        buffer = ""
        while True:
            # ler o que tiver no buffer (ou 1 byte)
            try:
                data = ser.read(ser.in_waiting or 1)
                if not data:
                    time.sleep(0.005)
                    continue
                buffer += data.decode(errors='ignore')
            except Exception as e:
                print(f"Erro de leitura bruta em {campo}: {e}")
                time.sleep(0.05)
                continue

            linhas = buffer.split('\n')
            buffer = linhas[-1]  # sobra parcial

            for linha in linhas[:-1]:
                linha = linha.strip()
                if not linha:
                    continue

                if filtro_nmea == "ALL":
                    ultima_sentenca[campo] = linha

                elif linha.startswith('$'):
                    if filtro_nmea is None or linha.startswith(f"${filtro_nmea}"):
                        ultima_sentenca[campo] = linha

                    # Captura precisão do GPGST
                    if linha.startswith("$GPGST"):
                        match = re.match(gpgst_pattern, linha)
                        if match:
                            # match.groups() => (time, rms, lat_err, lon_err, alt_err)
                            _, rms, lat_err, lon_err, alt_err = match.groups()
                            ultima_precisao.update({
                                "rms": rms,
                                "lat_err": lat_err,
                                "lon_err": lon_err,
                                "alt_err": alt_err
                            })
            # pequena pausa para não consumir 100% CPU
            time.sleep(0.005)

    except Exception as e:
        print(f"Erro na leitura serial ({campo}): {e}")

# ==============================
# ENVIO PARA FIREBASE (ASSÍNCRONO)
# ==============================
def sincronizar_envio():
    while True:
        try:
            if not fila_envio.empty():
                dados = fila_envio.get()
                # batch update para reduzir requisições
                try:
                    db.update({
                        "gnss/raw": dados["sentencas"].get("raw", ""),
                        "gnss/raw2": dados["sentencas"].get("raw2", ""),
                        "gnss_precision": dados["precisao"]
                    })
                    if DEBUG:
                        print("Firebase atualizado (batch).")
                except Exception as e:
                    # fallback para updates separados em caso de erro
                    try:
                        db.child("gnss").update(dados["sentencas"])
                        db.child("gnss_precision").update(dados["precisao"])
                        if DEBUG:
                            print("Firebase atualizado (separado).")
                    except Exception as e2:
                        print(f"Erro ao enviar para Firebase (fallback): {e2}")
        except Exception as e:
            print(f"Erro na sincronização de envio: {e}")
        time.sleep(0.02)  # tentar ~50 Hz quando houver dados na fila

# ==============================
# AGENDAR ENVIOS PERIÓDICOS
# ==============================
def agendar_envio():
    global ultima_sentenca, ultima_precisao
    while True:
        try:
            # se a fila estiver cheia, descarta o mais antigo e insere o mais novo
            if fila_envio.full():
                try:
                    _ = fila_envio.get_nowait()
                except:
                    pass
            fila_envio.put({
                "sentencas": {
                    "raw": ultima_sentenca["raw"],
                    "raw2": ultima_sentenca["raw2"]
                },
                "precisao": ultima_precisao.copy()
            })
            if DEBUG:
                print(f"Agendado: {ultima_sentenca['raw']} | {ultima_sentenca['raw2']}")
        except Exception as e:
            print(f"Erro no agendamento: {e}")
        time.sleep(intervalo_envio_ms / 1000.0)

# ==============================
# MONITORAR COMANDOS REMOTOS
# ==============================
def monitorar_comandos():
    global ser1, ser2
    ultimo_comando1 = ""
    ultimo_comando2 = ""

    while True:
        try:
            comando1 = None
            comando2 = None
            try:
                comando1 = db.child("receiver").child("comando").get().val()
            except Exception:
                pass
            try:
                comando2 = db.child("receiver").child("comando2").get().val()
            except Exception:
                pass

            if comando1 and comando1 != ultimo_comando1:
                print(f"[COMANDO 1] Novo comando: {comando1}")
                if ser1:
                    try:
                        ser1.write(comando1.encode('utf-8') + b'\r\n')
                    except Exception as e:
                        print(f"Falha ao enviar comando1 para serial: {e}")
                ultimo_comando1 = comando1

            if comando2 and comando2 != ultimo_comando2:
                print(f"[COMANDO 2] Novo comando: {comando2}")
                if ser2:
                    try:
                        ser2.write(comando2.encode('utf-8') + b'\r\n')
                    except Exception as e:
                        print(f"Falha ao enviar comando2 para serial: {e}")
                ultimo_comando2 = comando2

        except Exception as e:
            print(f"Erro ao monitorar comandos: {e}")
        time.sleep(0.2)

# ==============================
# FUNÇÃO PRINCIPAL
# ==============================
def iniciar_terminal():
    global intervalo_envio_ms, ser1, ser2

    print("=== Leitura NMEA Dupla com Envio Rápido para Firebase ===\n")

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

        print("\nEscolha a velocidade de envio para o Firebase:")
        print("1: Muito rápido (50 ms)")
        print("2: Rápido (100 ms)")
        print("3: Normal (500 ms)")
        print("4: Lento (1000 ms)")
        print("5: Muito lento (2000 ms)")
        velocidade = input("Digite o número da velocidade desejada (1 a 5): ")

        velocidades_ms = [50, 100, 500, 1000, 2000]
        try:
            idx_vel = int(velocidade) - 1
            intervalo_envio_ms = velocidades_ms[idx_vel] if 0 <= idx_vel < len(velocidades_ms) else 1000
        except:
            intervalo_envio_ms = 1000

        comandos = carregar_comandos()

        print(f"\nIniciando leitura e envio a cada {intervalo_envio_ms} ms...\n")

        try:
            ser1 = serial.Serial(porta1, baud1, timeout=0.1)
            ser2 = serial.Serial(porta2, baud2, timeout=0.1)
        except Exception as e:
            print(f"Erro ao abrir portas seriais: {e}")
            return

        # threads
        threading.Thread(target=leitura_serial, args=(ser1, "raw", comandos, filtro), daemon=True).start()
        threading.Thread(target=leitura_serial, args=(ser2, "raw2", comandos, filtro), daemon=True).start()
        threading.Thread(target=sincronizar_envio, daemon=True).start()
        threading.Thread(target=agendar_envio, daemon=True).start()
        threading.Thread(target=monitorar_comandos, daemon=True).start()

        # loop principal para manter o programa vivo e permitir KeyboardInterrupt
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário. Fechando portas seriais...")
            try:
                if ser1 and ser1.is_open:
                    ser1.close()
                if ser2 and ser2.is_open:
                    ser2.close()
            except Exception as e:
                print(f"Erro ao fechar seriais: {e}")
            print("Encerrado.")
            return

    except Exception as e:
        print(f"Erro na inicialização: {e}")
        try:
            if ser1 and ser1.is_open:
                ser1.close()
            if ser2 and ser2.is_open:
                ser2.close()
        except:
            pass

# ==============================
# PONTO DE ENTRADA
# ==============================
if __name__ == "__main__":
    iniciar_terminal()