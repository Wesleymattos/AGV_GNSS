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
    "storageBucket": "log--analyzer-web.firebasestorage.app",
    "messagingSenderId": "908592112855",
    "appId": "1:908592112855:web:ae60fc51e47a66390f3c92",
    "measurementId": "G-PEWMF5LTLQ"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

baud_rates = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000, 460800]
ultima_sentenca = {"raw": "", "raw2": ""}
intervalo_envio_ms = 1000

ser1 = None
ser2 = None

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
    print(f"{len(filtros_disponiveis)+1}: Sem filtro (enviar todas as sentenças NMEA)")
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

def leitura_serial(ser, campo, comandos_txt, filtro_nmea):
    global ultima_sentenca
    try:
        if comandos_txt:
            time.sleep(1)
            for cmd in comandos_txt:
                ser.write(cmd.encode('utf-8') + b'\r\n')
                print(f"Comando enviado: {cmd}")
                time.sleep(0.2)
        buffer = ""
        while True:
            buffer += ser.read(ser.in_waiting or 1).decode(errors='ignore')
            linhas = buffer.split('\n')
            buffer = linhas[-1]
            for linha in linhas[:-1]:
                linha = linha.strip()
                if filtro_nmea == "ALL":
                    ultima_sentenca[campo] = linha
                elif linha.startswith('$'):
                    if filtro_nmea is None or linha.startswith(f"${filtro_nmea}"):
                        ultima_sentenca[campo] = linha
            time.sleep(0.05)
    except Exception as e:
        print(f"Erro na leitura serial: {e}")

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

def monitorar_comandos():
    global ser1, ser2
    ultimo_comando1 = ""
    ultimo_comando2 = ""

    while True:
        try:
            comando1 = db.child("receiver").child("comando").get().val()
            comando2 = db.child("receiver").child("comando2").get().val()

            if comando1 and comando1 != ultimo_comando1:
                print(f"[COMANDO 1] Novo comando detectado: {comando1}")
                if ser1:
                    ser1.write(comando1.encode('utf-8') + b'\r\n')
                    print(f"Comando enviado para porta 1: {comando1}")
                ultimo_comando1 = comando1

            if comando2 and comando2 != ultimo_comando2:
                print(f"[COMANDO 2] Novo comando detectado: {comando2}")
                if ser2:
                    ser2.write(comando2.encode('utf-8') + b'\r\n')
                    print(f"Comando enviado para porta 2: {comando2}")
                ultimo_comando2 = comando2

        except Exception as e:
            print(f"Erro ao monitorar comandos: {e}")

        time.sleep(0.5)

def iniciar_terminal():
    global intervalo_envio_ms, ser1, ser2
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

        print("\nEscolha a velocidade de envio para o Firebase:")
        print("1: Muito rápido (200 ms)")
        print("2: Rápido (500 ms)")
        print("3: Normal (1000 ms)")
        print("4: Lento (2000 ms)")
        print("5: Muito lento (5000 ms)")
        velocidade = input("Digite o número da velocidade desejada (1 a 5): ")
        try:
            velocidades_ms = [200, 500, 1000, 2000, 5000]
            idx_vel = int(velocidade) - 1
            if 0 <= idx_vel < len(velocidades_ms):
                intervalo_envio_ms = velocidades_ms[idx_vel]
            else:
                print("Opção inválida. Usando padrão de 1000 ms.")
        except:
            print("Entrada inválida. Usando padrão de 1000 ms.")

        comandos = carregar_comandos()
        print(f"\nIniciando leitura e envio sincronizado a cada {intervalo_envio_ms} ms...")

        ser1 = serial.Serial(porta1, baud1, timeout=1)
        ser2 = serial.Serial(porta2, baud2, timeout=1)

        threading.Thread(target=leitura_serial, args=(ser1, "raw", comandos, filtro), daemon=True).start()
        threading.Thread(target=leitura_serial, args=(ser2, "raw2", comandos, filtro), daemon=True).start()
        threading.Thread(target=sincronizar_envio, daemon=True).start()
        threading.Thread(target=monitorar_comandos, daemon=True).start()

        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    iniciar_terminal()
