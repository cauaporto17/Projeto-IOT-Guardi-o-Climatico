import json
import random
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import pygame
import threading

ARQUIVO_NUVEM = "nuvem_iot.json"
LOGO_PATH = "Guardião logo.png"
SOM_ALERTA = "alerta.mp3"

class GuardianClimaticoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌡️ Guardião Climático")
        self.root.geometry("950x750")
        self.root.configure(bg="#EAF6F6")


        pygame.mixer.init()

        self.exibir_logo()

        ttk.Label(
            self.root,
            text="Painel de Monitoramento IoT",
            font=("Segoe UI", 18, "bold"),
            background="#EAF6F6",
            foreground="#004E64"
        ).pack(pady=10)

        botoes_frame = ttk.Frame(self.root)
        botoes_frame.pack(pady=10)
        ttk.Button(botoes_frame, text="Gerar Relatório em PDF", command=self.gerar_relatorio_pdf).grid(row=0, column=0, padx=10)

        self.alerta_label = ttk.Label(
            self.root,
            text="Sem alertas no momento.",
            background="#EAF6F6",
            font=("Segoe UI", 11, "bold"),
            foreground="#00796B"
        )
        self.alerta_label.pack(pady=10)

        self.frame_graficos = ttk.Frame(self.root)
        self.frame_graficos.pack(fill="both", expand=True)


        self.temperaturas = []
        self.umidades = []
        self.leituras = []


        self.fig, (self.ax_temp, self.ax_umid) = plt.subplots(1, 2, figsize=(10, 4))
        self.fig.tight_layout(pad=4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graficos)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


        self.auto_refresh_dashboard()

    def exibir_logo(self):
        try:
            img = Image.open(LOGO_PATH)
            img = img.resize((180, 180))
            logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(self.root, image=logo, bg="#EAF6F6")
            label_logo.image = logo
            label_logo.pack(pady=10)
        except Exception as e:
            print("Erro ao carregar a logo:", e)

    def gerar_novas_leituras(self):

        leitura = {
            "timestamp": datetime.now().isoformat(),
            "temperatura": round(random.uniform(18, 35), 2),
            "umidade": round(random.uniform(35, 75), 2)
        }

        self.temperaturas.append(leitura["temperatura"])
        self.umidades.append(leitura["umidade"])
        self.leituras.append(len(self.temperaturas))


        if len(self.temperaturas) > 10:
            self.temperaturas.pop(0)
            self.umidades.pop(0)
            self.leituras.pop(0)


        dados = [{"timestamp": datetime.now().isoformat(),
                  "temperatura": t,
                  "umidade": u} for t, u in zip(self.temperaturas, self.umidades)]
        with open(ARQUIVO_NUVEM, "w") as f:
            json.dump(dados, f, indent=4)

    def atualizar_dashboard(self):
        self.ax_temp.clear()
        self.ax_umid.clear()

        self.ax_temp.plot(self.leituras, self.temperaturas, marker="o", color="orange")
        self.ax_temp.set_title("Temperatura (°C)", fontsize=12)
        self.ax_temp.grid(True)

        self.ax_umid.plot(self.leituras, self.umidades, marker="o", color="blue")
        self.ax_umid.set_title("Umidade (%)", fontsize=12)
        self.ax_umid.grid(True)

        self.canvas.draw()


        if self.temperaturas and self.umidades:
            self.verificar_alertas(self.temperaturas[-1], self.umidades[-1])

    def auto_refresh_dashboard(self):

        self.gerar_novas_leituras()
        self.atualizar_dashboard()
        self.root.after(5000, self.auto_refresh_dashboard)  # Repetir a cada 5 segundos

    def verificar_alertas(self, temperatura, umidade):
        alertas = []
        tocar_som = False

        if temperatura > 30:
            alertas.append(f"⚠️ Temperatura alta: {temperatura:.1f}°C")
            tocar_som = True
        elif temperatura < 18:
            alertas.append(f"❄️ Temperatura baixa: {temperatura:.1f}°C")
            tocar_som = True

        if umidade < 40:
            alertas.append(f"💧 Umidade muito baixa: {umidade:.1f}%")
            tocar_som = True
        elif umidade > 70:
            alertas.append(f"💦 Umidade alta: {umidade:.1f}%")
            tocar_som = True

        if alertas:
            alerta_texto = "\n".join(alertas)
            self.alerta_label.config(text=alerta_texto, foreground="red")
            messagebox.showwarning("Alerta Inteligente", alerta_texto)

            if tocar_som:

                def tocar_som_thread():
                    pygame.mixer.music.load(SOM_ALERTA)
                    pygame.mixer.music.play()
                threading.Thread(target=tocar_som_thread, daemon=True).start()
        else:
            self.alerta_label.config(text="✅ Condições normais.", foreground="#00796B")

    def gerar_relatorio_pdf(self):
        try:
            with open(ARQUIVO_NUVEM, "r") as f:
                dados = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'nuvem_iot.json' não encontrado.")
            return

        temperaturas = [d["temperatura"] for d in dados]
        umidades = [d["umidade"] for d in dados]

        media_temp = sum(temperaturas) / len(temperaturas)
        media_umid = sum(umidades) / len(umidades)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
        ax1.plot(temperaturas, marker="o", color="orange")
        ax1.set_title("Temperatura (°C)")
        ax1.grid(True)
        ax2.plot(umidades, marker="o", color="blue")
        ax2.set_title("Umidade (%)")
        ax2.grid(True)

        grafico_path = "grafico_temp_umid.png"
        plt.tight_layout()
        plt.savefig(grafico_path)
        plt.close()

        pdf_path = "relatorio_guardiao_climatico.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("<b>Guardião Climático</b>", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Média de Temperatura:</b> {media_temp:.2f} °C", styles["Normal"]))
        story.append(Paragraph(f"<b>Média de Umidade:</b> {media_umid:.2f} %", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Temperatura Máxima:</b> {max(temperaturas):.2f} °C", styles["Normal"]))
        story.append(Paragraph(f"<b>Temperatura Mínima:</b> {min(temperaturas):.2f} °C", styles["Normal"]))
        story.append(Paragraph(f"<b>Umidade Máxima:</b> {max(umidades):.2f} %", styles["Normal"]))
        story.append(Paragraph(f"<b>Umidade Mínima:</b> {min(umidades):.2f} %", styles["Normal"]))
        story.append(Spacer(1, 20))
        story.append(RLImage(grafico_path, width=400, height=180))

        doc.build(story)
        messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nArquivo: {pdf_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GuardianClimaticoApp(root)
    root.mainloop()
