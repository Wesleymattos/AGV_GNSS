import requests
import time
import serial
import serial.tools.list_ports
 
firebase_url = "https://log--analyzer-web-default-rtdb.firebaseio.com/agv.json"
 
def gerar_comandos(agv_data):
    comandos = []
    for chave, valor in agv_data.items():
        if isinstance(valor, bool):
            comando = f"{chave}_ON" if valor else f"{chave}_OFF"
            comandos.append(comando)
    return comandos
 
def encontrar_esp32():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "CP210" in port.description or "CH340" in port.description:
            return port.device
    return None
 
def conectar_esp32():
    porta = encontrar_esp32()
    if porta:
        try:
            ser = serial.Serial(porta, 115200, timeout=1)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            print(f"[OK] ESP32 conectado na porta {porta}")
            return ser
        except Exception as e:
            print(f"[ERRO] Falha ao conectar: {e}")
    else:
        print("[AGUARDANDO] ESP32 não encontrado. Conecte via USB...")
    return None
 
def enviar_comando(cmd, ser):
    try:
        ser.write((cmd + '\n').encode())
        resposta = ser.readline()
        resposta_decodificada = resposta.decode('utf-8', errors='ignore').strip()
        print(f"Comando: {cmd} | Resposta: {resposta_decodificada if resposta_decodificada else 'Sem resposta'}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar comando {cmd}: {e}")
        raise e
 
def ler_agv():
    try:
        response = requests.get(firebase_url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro HTTP: {response.status_code}")
    except Exception as e:
        print(f"[ERRO] Falha ao acessar Firebase: {e}")
        raise e
 
def iniciar_monitoramento():
    print("[INICIANDO] Monitoramento da árvore 'agv'...")
    while True:
        ser = conectar_esp32()
        if not ser:
            time.sleep(3)
            continue  # tenta de novo
 
        print("[MONITORANDO] Arvore 'agv' e comandos para ESP32...\n")
        try:
            while ser and ser.is_open:
                agv_data = ler_agv()
                comandos = gerar_comandos(agv_data)
                for cmd in comandos:
                    enviar_comando(cmd, ser)
                print("-" * 40)
                time.sleep(2)
 
        except Exception as e:
            print(f"[ERRO] {e}")
            print("[REINICIANDO] Reconectando em 3 segundos...\n")
            try:
                if ser and ser.is_open:
                    ser.close()
            except:
                pass
            time.sleep(3)
 
if __name__ == "__main__":
    iniciar_monitoramento()
