import random
import json
import time
from datetime import datetime

def gerar_dado_sensor():

    temp = round(random.uniform(20.0, 30.0), 2)  # temperatura entre 20°C e 30°C
    hum = round(random.uniform(40.0, 70.0), 2)   # umidade entre 40% e 70%
    return {
        "timestamp": datetime.now().isoformat(),
        "temperatura": temp,
        "umidade": hum
    }

def enviar_para_nuvem():

    dados = []
    for i in range(10):
        dado = gerar_dado_sensor()
        dados.append(dado)
        print(f"Leitura {i+1}: {dado}")
        time.sleep(0.5)  # simula intervalo de leitura do sensor

    with open("nuvem_iot.json", "w") as f:
        json.dump(dados, f, indent=4)

    print("\ Dados enviados para a nuvem (arquivo nuvem_iot.json).")

if __name__ == "__main__":
    enviar_para_nuvem()