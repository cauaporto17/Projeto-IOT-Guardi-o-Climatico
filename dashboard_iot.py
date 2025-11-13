import json
import matplotlib.pyplot as plt

def exibir_dashboard():

    try:
        with open("nuvem_iot.json", "r") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print("Arquivo 'nuvem_iot.json' não encontrado. Execute primeiro o sensor_iot.py")
        return

    temperaturas = [d["temperatura"] for d in dados]
    umidades = [d["umidade"] for d in dados]
    leituras = list(range(1, len(dados) + 1))

    # Gráfico de Temperatura
    plt.figure(figsize=(8, 4))
    plt.plot(leituras, temperaturas, marker="o", color="orange")
    plt.title("Monitor de Temperatura (Simulação IoT)")
    plt.xlabel("Leitura")
    plt.ylabel("Temperatura (°C)")
    plt.grid()
    plt.show()

    # Gráfico de Umidade
    plt.figure(figsize=(8, 4))
    plt.plot(leituras, umidades, marker="o", color="blue")
    plt.title("Monitor de Umidade (Simulação IoT)")
    plt.xlabel("Leitura")
    plt.ylabel("Umidade (%)")
    plt.grid()
    plt.show()

if __name__ == "__main__":
    exibir_dashboard()