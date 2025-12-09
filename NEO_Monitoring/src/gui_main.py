# src/gui_main.py
"""
Aplicação GUI (Tkinter) para o NEO Monitoring.

Fluxo:
  1) Janela de login de administrador
  2) Janela de configuração/ligação à base de dados
  3) Janela principal com menu de botões
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import random
import webbrowser
import threading
import queue
import time


from PIL import Image, ImageTk
import pyodbc

from auth import (
    credenciais_admin_validas,
    criar_utilizador,
    alterar_credenciais,
    existe_utilizador,
)
from db import (
    construir_connection_string,
    ligar_base_dados,
    LigacaoBDFalhada,
    DEFAULT_DRIVER,
)

from services.import_esa import (
    importar_risk_list,
    importar_special_risk_list,
    importar_past_impactors,
    importar_removed_from_risk,
    importar_upcoming_cl_app,
    importar_search_result,
)

from services.insercao import asteroides_existem, importar_neo_csv, importar_mpcorb_dat
from services import consultas

CONFIG_FILE = "config.json"


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Draw a rounded rectangle on a canvas."""
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


class BackgroundAnimation:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.stars = []
        self.meteors = []
        self.running = True
        
        self.create_stars()
        self.animate()

    def update_dimensions(self, width, height):
        self.width = width
        self.height = height

    def create_stars(self):
        # Limpar estrelas existentes se houver (para resize drástico? Não, apenas adicionamos mais se crescer? 
        # Simplificação: manter as existentes e o spawn de novas usa as novas dimensões.
        # Mas se a janela crescer muito, pode ficar vazio.
        # Vamos apenas garantir que temos estrelas suficientes.
        if len(self.stars) < 100:
            for _ in range(100 - len(self.stars)):
                self.spawn_star()
        elif not self.stars:
             for _ in range(100):
                self.spawn_star()

    def spawn_star(self):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        size = random.randint(1, 2)
        color = random.choice(["#ffffff", "#d4fbff", "#ffe9c4", "#8a8a8a"])
        star = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
        self.stars.append(star)

    def animate(self):
        if not self.running:
            return

        # Mover estrelas lentamente para a esquerda
        for star in self.stars:
            self.canvas.move(star, -0.1, 0)
            pos = self.canvas.coords(star)
            if pos and pos[2] < 0:
                self.canvas.move(star, self.width, 0)
            # Se a estrela estiver fora da altura (resize), trazer de volta?
            if pos and pos[3] > self.height:
                 self.canvas.move(star, 0, -self.height)


        # Criar meteoros aleatoriamente
        if random.random() < 0.01:  # 1% de chance por frame
            self.spawn_meteor()

        # Mover meteoros
        for m in self.meteors[:]:
            self.canvas.move(m, -5, 3)
            pos = self.canvas.coords(m)
            # Se sair do ecrã, remover
            if pos and (pos[0] < -50 or pos[1] > self.height + 50):
                self.canvas.delete(m)
                self.meteors.remove(m)

        self.canvas.after(30, self.animate)

    def spawn_meteor(self):
        x = random.randint(self.width // 2, self.width + 50)
        y = random.randint(-50, self.height // 2)
        length = random.randint(20, 50)
        # Meteoro como uma linha branca
        meteor = self.canvas.create_line(x, y, x-length, y+length*0.6, fill="white", width=2)
        self.meteors.append(meteor)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("NEO Monitoring")
        self.geometry("1440x900")
        self.resizable(True, True) # Permitir resize

        # Estado partilhado
        self.admin_user: str | None = None
        self.db_conn: pyodbc.Connection | None = None
        self.dark_mode = True 
        self.config = self.load_config()
        self.current_frame_name = "LoginFrame"
        self.current_frame = None

        # Carregar imagens
        self.load_images()

        # Canvas para fundo animado
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#050510")
        self.canvas.pack(fill="both", expand=True)
        
        self.bg_anim = BackgroundAnimation(self.canvas, 800, 600)

        # Top Bar Widgets (agora no canvas)
        self.lbl_welcome = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.btn_theme = ttk.Button(self, text="☀️", width=3, command=self.toggle_theme)
        
        # Botão de Logout (criado mas não colocado inicialmente)
        self.btn_logout = ttk.Button(self, text="🏃🚪", width=4, command=self.on_logout)

        # Colocar widgets da top bar no canvas
        self.canvas.create_window(10, 10, window=self.lbl_welcome, anchor="nw", tags="top_bar_left")
        self.canvas.create_window(790, 10, window=self.btn_theme, anchor="ne", tags="top_bar_right")

        self.frames: dict[str, tk.Frame] = {}

        # Criar frames
        for FrameClass in (LoginFrame, DbConfigFrame, MainMenuFrame, InsercaoESAFrame, UserConfigFrame, LoadingFrame):
            frame = FrameClass(parent=self, controller=self)
            self.frames[FrameClass.__name__] = frame

        # Configurar estilos (Theme)
        self.style = ttk.Style(self)
        self.setup_theme()
        
        self.show_frame("LoginFrame")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Verificar se o evento é da janela principal
        if event.widget == self:
            w, h = event.width, event.height
            self.bg_anim.update_dimensions(w, h)
            
            # Atualizar posições
            self.canvas.coords("top_bar_right", w - 10, 10)
            
            if self.current_frame_name != "LoginFrame" and self.img_logo_icon:
                 self.canvas.coords("corner_icon", 10, h - 10)
            
            # Atualizar posição do botão de logout se visível
            if self.current_frame_name == "MainMenuFrame":
                self.canvas.coords("logout_btn", w - 10, h - 10)

            # Re-centrar o cartão
            self.update_card_position()

    def on_frame_configure(self, event):
        # Quando o frame muda de tamanho, atualizar o cartão
        self.update_card_position()

    def update_card_position(self):
        if not self.current_frame:
            return

        # Obter dimensões da janela
        w = self.winfo_width()
        h = self.winfo_height()
        if w == 1: w, h = 800, 600

        # Obter dimensões do frame atual (tamanho desejado)
        fw = self.current_frame.winfo_reqwidth()
        fh = self.current_frame.winfo_reqheight()

        # Tamanho do cartão = frame + padding
        card_w = fw + 40
        card_h = fh + 40
        
        # Centrar
        x1 = (w - card_w) / 2
        y1 = (h - card_h) / 2 + 20 # Offset top bar
        x2 = x1 + card_w
        y2 = y1 + card_h
        
        # Atualizar rectangulo
        self.canvas.delete("card_bg")
        bg_color = "#2e2e2e" if self.dark_mode else "#f0f0f0"
        
        create_rounded_rect(self.canvas, x1, y1, x2, y2, radius=20, fill=bg_color, tags="card_bg")
        self.canvas.tag_lower("card_bg")
        
        # Atualizar posição do frame
        self.canvas.coords("current_frame", w/2, h/2 + 10)

    def load_images(self):
        self.img_logo_full = None
        self.img_logo_icon = None
        
        try:
            # Obter o diretório do script atual e voltar um nível para a raiz do projeto
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            assets_dir = os.path.join(project_root, "assets")
            
            logo_full_path = os.path.join(assets_dir, "logo_full.jpg")
            logo_icon_path = os.path.join(assets_dir, "logo_icon.jpg")
            
            if os.path.exists(logo_full_path):
                pil_img = Image.open(logo_full_path)
                w_percent = (300 / float(pil_img.size[0]))
                h_size = int((float(pil_img.size[1]) * float(w_percent)))
                pil_img = pil_img.resize((300, h_size), Image.Resampling.LANCZOS)
                self.img_logo_full = ImageTk.PhotoImage(pil_img)

            if os.path.exists(logo_icon_path):
                pil_img = Image.open(logo_icon_path)
                h_percent = (60 / float(pil_img.size[1]))
                w_size = int((float(pil_img.size[0]) * float(h_percent)))
                pil_img = pil_img.resize((w_size, 60), Image.Resampling.LANCZOS)
                self.img_logo_icon = ImageTk.PhotoImage(pil_img)
        except Exception as e:
            print(f"Erro ao carregar imagens: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f)
        except Exception:
            pass

    def setup_theme(self):
        self.style.theme_use("clam")
        
        if self.dark_mode:
            bg_color = "#2e2e2e" # Cor do cartão
            fg_color = "#ffffff"
            entry_bg = "#404040"
            btn_bg = "#505050"
            active_bg = "#606060"
            canvas_bg = "#050510"
        else:
            bg_color = "#f0f0f0" # Cor do cartão
            fg_color = "#000000"
            entry_bg = "#ffffff"
            btn_bg = "#e0e0e0"
            active_bg = "#d0d0d0"
            canvas_bg = "#101030"

        self.configure(bg=canvas_bg)
        if hasattr(self, "canvas"):
            self.canvas.configure(bg=canvas_bg)
            # Atualizar cor do cartão atual
            self.canvas.itemconfig("card_bg", fill=bg_color)

        # Configurar estilos
        self.style.configure(".", background=bg_color, foreground=fg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TButton", background=btn_bg, foreground=fg_color, borderwidth=1)
        self.style.map("TButton", background=[("active", active_bg)])
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color)

        # Atualizar frames
        for frame in getattr(self, "frames", {}).values():
            frame.configure(style="TFrame")

        # Top Bar Widgets - tentar "transparência" combinando com o fundo do canvas
        # Nota: TButton e TLabel não suportam bg transparente real.
        # Vamos definir o bg deles para a cor do canvas.
        self.lbl_welcome.configure(background=canvas_bg, foreground="#ffffff") # Sempre branco no espaço?
        # O botão de tema precisa de contraste
        # Se for TButton, ele usa o style. Vamos criar um style especifico para o botao de tema?
        self.style.configure("Theme.TButton", background=btn_bg, foreground=fg_color)
        self.btn_theme.configure(style="Theme.TButton")
        
        # Mas o label de welcome tem de ter o fundo do canvas
        self.style.configure("Welcome.TLabel", background=canvas_bg, foreground="#ffffff")
        self.lbl_welcome.configure(style="Welcome.TLabel")


    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.btn_theme.configure(text="☀️" if self.dark_mode else "🌙")
        self.setup_theme()

    def show_frame(self, name: str):
        # Unbind previous frame event
        if self.current_frame:
            self.current_frame.unbind("<Configure>")

        self.current_frame_name = name
        self.current_frame = self.frames[name]
        
        # Bind configure event to update card size dynamically
        self.current_frame.bind("<Configure>", self.on_frame_configure)

        # Limpar janela atual do canvas (card e frame)
        self.canvas.delete("current_frame")
        self.canvas.delete("card_bg")
        self.canvas.delete("corner_icon")
        self.canvas.delete("logout_btn")
        
        frame = self.frames[name]
        frame.tkraise()
        
        # Obter dimensões atuais
        w = self.winfo_width()
        h = self.winfo_height()
        if w == 1: w, h = 800, 600 # Default startup

        # Desenhar o cartão arredondado (usa update_card_position logic)
        self.update_card_position()
        
        # Adicionar frame ao canvas centrado no cartão
        self.canvas.create_window(w/2, h/2 + 10, window=frame, tags="current_frame", anchor="center")
        
        # Icon logic
        if name != "LoginFrame" and self.img_logo_icon:
             self.canvas.create_image(10, h - 10, image=self.img_logo_icon, anchor="sw", tags="corner_icon")

        # Logout Button Logic (apenas no MainMenuFrame)
        if name == "MainMenuFrame":
            self.canvas.create_window(w - 10, h - 10, window=self.btn_logout, anchor="se", tags="logout_btn")
        
        # Atualizar UI baseada no frame
        if name == "LoginFrame":
            self.lbl_welcome.configure(text="")
            self.admin_user = None
            if self.db_conn:
                try:
                    self.db_conn.close()
                except:
                    pass
                self.db_conn = None

    def set_admin_user(self, username: str):
        self.admin_user = username
        self.lbl_welcome.configure(text=f"Bem-vindo, {username}")

    def set_db_connection(self, conn: pyodbc.Connection):
        self.db_conn = conn

    def depois_de_ligar_bd(self):
        """
        Chamado depois de a ligação à BD estar estabelecida.
        Se a tabela ASTEROIDE estiver vazia, pergunta se pretende importar o neo.csv.
        No fim, mostra o menu principal.
        """
        if self.db_conn is None:
            return

        try:
            # Se já existirem asteroides, não chateia com o neo.csv
            if asteroides_existem(self.db_conn):
                self.show_frame("MainMenuFrame")
                return

            # BD vazia em ASTEROIDE -> perguntar se quer importar agora
            if messagebox.askyesno(
                "Importar dados iniciais",
                "Ainda não existem asteroides na base de dados.\n"
                "Pretende importar agora o ficheiro neo.csv?"
            ):
                # tentar abrir por defeito na pasta docs, se existir
                initialdir = os.path.join(os.getcwd(), "docs")
                if not os.path.isdir(initialdir):
                    initialdir = os.getcwd()

                caminho = filedialog.askopenfilename(
                    title="Selecione o ficheiro neo.csv",
                    initialdir=initialdir,
                    filetypes=[("Ficheiros CSV", "*.csv"), ("Todos os ficheiros", "*.*")],
                )

                if caminho:
                    self.start_import_thread(caminho)
                else:
                    messagebox.showwarning(
                        "Importação cancelada",
                        "Não foi seleccionado nenhum ficheiro. "
                        "Pode importar mais tarde na 'Aplicação de Inserção'."
                    )
                    self.show_frame("MainMenuFrame")
            else:
                 # Em qualquer caso, segue para o menu principal
                self.show_frame("MainMenuFrame")

        except Exception as exc:
            messagebox.showerror(
                "Erro na importação inicial",
                f"Ocorreu um erro ao verificar/importar o neo.csv:\n{exc}"
            )
            self.show_frame("MainMenuFrame")

    def start_import_thread(self, csv_path):
        self.show_frame("LoadingFrame")
        self.import_queue = queue.Queue()
        
        def run_import():
            try:
                def cb(curr, tot, el):
                    self.import_queue.put(("progress", curr, tot, el))
                
                count = importar_neo_csv(self.db_conn, csv_path, progress_callback=cb)
                self.import_queue.put(("done", count))
            except Exception as e:
                self.import_queue.put(("error", str(e)))

        threading.Thread(target=run_import, daemon=True).start()
        self.check_import_queue()

    def check_import_queue(self):
        try:
            while True:
                msg = self.import_queue.get_nowait()
                if msg[0] == "progress":
                    _, curr, tot, el = msg
                    if "LoadingFrame" in self.frames and isinstance(self.frames["LoadingFrame"], LoadingFrame):
                        self.frames["LoadingFrame"].update_progress(curr, tot, el)
                elif msg[0] == "done":
                    count = msg[1]
                    messagebox.showinfo("Importação concluída", f"Foram inseridos {count} registos.")
                    self.show_frame("MainMenuFrame")
                    return
                elif msg[0] == "error":
                    err = msg[1]
                    messagebox.showerror("Erro", f"Erro na importação: {err}")
                    self.show_frame("MainMenuFrame")
                    return
        except queue.Empty:
            pass
        
        self.after(100, self.check_import_queue)


    def on_logout(self):
        if messagebox.askyesno("Logout", "Deseja terminar a sessão?"):
            self.show_frame("LoginFrame")

    def on_close(self):
        if self.bg_anim:
            self.bg_anim.running = False
        if self.db_conn:
            try:
                self.db_conn.close()
            except Exception:
                pass
        self.destroy()

    def _fill_tree(self, tree: ttk.Treeview, cols, rows):
            """Atualiza o Treeview com colunas e linhas vindas do services/consultas."""
            tree["columns"] = cols
            tree["show"] = "headings"

            # Cabeçalhos
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, anchor="center", width=120)

            # Limpar linhas antigas
            for item in tree.get_children():
                tree.delete(item)

            # Inserir novas linhas
            for row in rows:
                tree.insert("", "end", values=[row[c] for c in cols])



class LoadingFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=40)
        
        self.lbl_title = ttk.Label(self, text="A Processar...", font=("Segoe UI", 16, "bold"))
        self.lbl_title.pack(pady=(0, 20))
        
        self.progress = ttk.Progressbar(self, mode='determinate', length=400)
        self.progress.pack(pady=10)
        
        self.lbl_status = ttk.Label(self, text="A iniciar...", font=("Segoe UI", 10))
        self.lbl_status.pack(pady=5)
        
        self.lbl_time = ttk.Label(self, text="Decorrido: 00:00 | Estimado: --:--", font=("Segoe UI", 9))
        self.lbl_time.pack(pady=5)

    def update_progress(self, current, total, elapsed):
        percent = (current / total) * 100
        self.progress['value'] = percent
        
        # Format elapsed
        el_min = int(elapsed // 60)
        el_sec = int(elapsed % 60)
        
        # Estimar ETA
        if current > 0:
            rate = current / elapsed
            remaining = total - current
            eta_seconds = remaining / rate
            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)
            eta_str = f"{eta_min:02d}:{eta_sec:02d}"
        else:
            eta_str = "--:--"

        self.lbl_status.configure(text=f"Processado: {current}/{total} ({percent:.1f}%)")
        self.lbl_time.configure(text=f"Decorrido: {el_min:02d}:{el_sec:02d} | Estimado: {eta_str}")
        self.update_idletasks()


class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        
        # Padding interno para não ficar colado às bordas do "cartão"
        self.configure(padding=20)

        # Imagem Logo Full
        if self.controller.img_logo_full:
            lbl_img = ttk.Label(self, image=self.controller.img_logo_full)
            lbl_img.grid(row=0, column=0, pady=(0, 20))

        titulo = ttk.Label(self, text="Login de administrador", font=("Segoe UI", 16, "bold"))
        titulo.grid(row=1, column=0, pady=(0, 20))

        self.msg = ttk.Label(self, text="Introduza as credenciais de administrador.")
        self.msg.grid(row=2, column=0, pady=(0, 20))

        form = ttk.Frame(self)
        form.grid(row=3, column=0, pady=10)

        ttk.Label(form, text="Utilizador:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_user = ttk.Entry(form, width=25)
        self.entry_user.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Palavra-passe:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_pass = ttk.Entry(form, show="*", width=25)
        self.entry_pass.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Bind Enter key
        self.entry_user.bind("<Return>", lambda e: self.on_login())
        self.entry_pass.bind("<Return>", lambda e: self.on_login())

        self.save_login_var = tk.BooleanVar()
        ttk.Checkbutton(form, text="Guardar dados", variable=self.save_login_var).grid(row=2, column=0, columnspan=2, pady=5)

        btn = ttk.Button(self, text="Entrar", command=self.on_login)
        btn.grid(row=4, column=0, pady=20)
        
        # Pre-fill se existir
        if "username" in self.controller.config:
            self.entry_user.insert(0, self.controller.config["username"])
            self.save_login_var.set(True)

    def on_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if credenciais_admin_validas(username, password):
            self.controller.set_admin_user(username)
            
            # Guardar preferência
            if self.save_login_var.get():
                self.controller.config["username"] = username
            else:
                self.controller.config.pop("username", None)
            self.controller.save_config()
            
            # Não mostramos popup, apenas avançamos
            self.controller.show_frame("DbConfigFrame")
            self.entry_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Erro de login", "Credenciais inválidas.")
            self.entry_pass.delete(0, tk.END)


class DbConfigFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=20)

        # Carregar defaults ou config
        cfg = self.controller.config.get("db", {})
        
        self.servidor_var = tk.StringVar(value=cfg.get("server", "localhost\\SQLEXPRESS"))
        self.base_dados_var = tk.StringVar(value=cfg.get("database", "BD_PL2_09"))
        self.auth_mode_var = tk.StringVar(value=cfg.get("auth_mode", "windows"))
        self.user_var = tk.StringVar(value=cfg.get("user", ""))
        self.pass_var = tk.StringVar(value=cfg.get("password", ""))
        self.ip_var = tk.StringVar(value=cfg.get("ip", "localhost"))
        self.port_var = tk.StringVar(value=cfg.get("port", "1433"))

        titulo = ttk.Label(self, text="Ligação à base de dados", font=("Segoe UI", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Grid para o formulário
        self.form = ttk.Frame(self)
        self.form.grid(row=1, column=0)

        row = 0
        row = 0
        self.lbl_servidor = ttk.Label(self.form, text="Servidor:")
        self.lbl_servidor.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        self.entry_servidor = ttk.Entry(self.form, textvariable=self.servidor_var, width=30)
        self.entry_servidor.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        # Campos IP e Porta (inicialmente ocultos ou não, dependendo do modo)
        self.lbl_ip = ttk.Label(self.form, text="IP:")
        self.lbl_ip.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        self.entry_ip = ttk.Entry(self.form, textvariable=self.ip_var, width=20)
        self.entry_ip.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        # Porta na mesma linha do IP ou linha abaixo? Vamos por linha abaixo para ser mais limpo ou ao lado?
        # Vamos por numa nova row para simplificar, ou usar um frame para IP e Porta na mesma linha.
        # Vou usar um frame para IP e Porta ficarem na mesma "linha lógica" do formulário se quiser, 
        # mas como estou a substituir o "Servidor", posso usar duas linhas.
        # O user pediu "Pedir o IP e a porta".
        
        # Vou colocar IP numa linha e Porta noutra para ser consistente com o layout vertical.
        row += 1
        self.lbl_port = ttk.Label(self.form, text="Porta:")
        self.lbl_port.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        self.entry_port = ttk.Entry(self.form, textvariable=self.port_var, width=10)
        self.entry_port.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        row += 1
        ttk.Label(self.form, text="Base de dados:").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        ttk.Entry(self.form, textvariable=self.base_dados_var, width=30).grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )

        row += 1
        ttk.Label(self.form, text="Autenticação:").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        
        auth_frame = ttk.Frame(self.form)
        auth_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        ttk.Radiobutton(
            auth_frame,
            text="Windows",
            variable=self.auth_mode_var,
            value="windows",
            command=self.on_auth_mode_change,
        ).pack(side="left", padx=(0, 10))
        
        ttk.Radiobutton(
            auth_frame,
            text="SQL Server",
            variable=self.auth_mode_var,
            value="sql",
            command=self.on_auth_mode_change,
        ).pack(side="left")

        # Widgets de user/pass (guardamos referências para esconder/mostrar)
        row += 1
        self.lbl_user_bd = ttk.Label(self.form, text="Utilizador BD:")
        self.lbl_user_bd.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        
        self.entry_user_bd = ttk.Entry(self.form, textvariable=self.user_var, width=25)
        self.entry_user_bd.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        row += 1
        self.lbl_pass_bd = ttk.Label(self.form, text="Palavra-passe BD:")
        self.lbl_pass_bd.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        
        self.entry_pass_bd = ttk.Entry(self.form, textvariable=self.pass_var, show="*", width=25)
        self.entry_pass_bd.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        # Botões
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, pady=20)

        ttk.Button(btn_frame, text="Voltar", command=self.on_back).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Testar ligação", command=self.on_testar_ligacao).pack(side="left", padx=5)

        # Estado inicial
        self.on_auth_mode_change()

    def on_auth_mode_change(self):
        modo = self.auth_mode_var.get()
        if modo == "sql":
            self.lbl_servidor.grid_remove()
            self.entry_servidor.grid_remove()
            
            self.lbl_ip.grid()
            self.entry_ip.grid()
            self.lbl_port.grid()
            self.entry_port.grid()

            self.lbl_user_bd.grid()
            self.entry_user_bd.grid()
            self.lbl_pass_bd.grid()
            self.entry_pass_bd.grid()
        else:
            self.lbl_ip.grid_remove()
            self.entry_ip.grid_remove()
            self.lbl_port.grid_remove()
            self.entry_port.grid_remove()

            self.lbl_servidor.grid()
            self.entry_servidor.grid()

            self.lbl_user_bd.grid_remove()
            self.entry_user_bd.grid_remove()
            self.lbl_pass_bd.grid_remove()
            self.entry_pass_bd.grid_remove()

    def on_back(self):
        self.controller.show_frame("LoginFrame")

    def on_testar_ligacao(self):
        base_dados = self.base_dados_var.get().strip()
        modo = self.auth_mode_var.get()

        if modo == "windows":
            servidor = self.servidor_var.get().strip()
            if not servidor:
                messagebox.showwarning("Dados em falta", "Indique o servidor.")
                return
        else:
            # Modo SQL
            ip = self.ip_var.get().strip()
            port = self.port_var.get().strip()
            if not ip or not port:
                messagebox.showwarning("Dados em falta", "Indique o IP e a Porta.")
                return
            servidor = f"{ip},{port}"

        if not base_dados:
            messagebox.showwarning("Dados em falta", "Indique a base de dados.")
            return

        trusted = modo == "windows"
        user = self.user_var.get().strip() if modo == "sql" else None
        pwd = self.pass_var.get() if modo == "sql" else None

        if modo == "sql" and (not user or not pwd):
            messagebox.showwarning(
                "Dados em falta",
                "No modo SQL Server tem de indicar utilizador e palavra-passe.",
            )
            return

        try:
            conn_str = construir_connection_string(
                servidor=servidor,
                base_dados=base_dados,
                utilizador=user,
                password=pwd,
                trusted_connection=trusted,
                driver=DEFAULT_DRIVER,
            )
            conn = ligar_base_dados(conn_str)
        except LigacaoBDFalhada as exc:
            messagebox.showerror("Erro de ligação", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Erro inesperado", f"Ocorreu um erro: {exc}")
            return

        # Sucesso
        # Sucesso
        self.controller.set_db_connection(conn)
        
        # Guardar config
        db_config = {
            "server": servidor,
            "database": base_dados,
            "auth_mode": modo,
            "user": user if user else "",
            "password": pwd if pwd else ""
        }
        
        if modo == "sql":
            db_config["ip"] = ip
            db_config["port"] = port
            # Atualizar servidor para o formato IP,Port para uso futuro se reverter para windows? 
            # Não, mantemos separado.
            
        self.controller.config["db"] = db_config
        self.controller.save_config()

        messagebox.showinfo("Ligação", "Ligação à base de dados estabelecida com sucesso.")
        self.controller.depois_de_ligar_bd()


class MainMenuFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=20)

        # Título no topo do cartão
        titulo = ttk.Label(self, text="Monitorização de NEOs", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=(0, 5))

        subtitulo = ttk.Label(self, text="Menu Principal")
        subtitulo.pack(pady=(0, 15))

        # Frame principal com 2 colunas: sidebar (esq) + conteúdo (dir)
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=0)   # sidebar
        main.columnconfigure(1, weight=1)   # conteúdo
        main.rowconfigure(0, weight=1)

        # Sidebar à esquerda
        sidebar = ttk.Frame(main)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        # Área de conteúdo à direita
        content = ttk.Frame(main)
        content.grid(row=0, column=1, sticky="nsew")
        self.content_frame = content

        # Botões de navegação
        botoes = [
            ("🏠  Home", self.on_home),
            ("📥  Aplicação de Inserção", self.on_insercao),
            ("⚠️  Aplicação de Alertas", self.on_alertas),
            ("📊  Aplicação de Monitorização", self.on_monitorizacao),
            ("🔎  Consultas gerais", self.on_consultas),
            ("⚙️  Configurar Utilizador", self.on_user_config),
            ("ℹ️  Créditos", self.on_creditos),
        ]

        for text, cmd in botoes:
            ttk.Button(sidebar, text=text, width=28, command=cmd).pack(fill="x", pady=4)

        # Widgets de conteúdo (título + texto + zona de links)
        self.content_title = ttk.Label(content, text="", font=("Segoe UI", 14, "bold"))
        self.content_title.pack(anchor="w", pady=(0, 10))

        self.content_body = ttk.Label(
            content,
            text="",
            justify="left",
            wraplength=380,
        )
        self.content_body.pack(anchor="nw")

        self.links_frame = ttk.Frame(content)
        self.links_frame.pack(anchor="nw", pady=(10, 0))

        # Frame DINÂMICO onde vamos pôr tabelas, notebooks, etc.
        self.data_frame = ttk.Frame(content)
        self.data_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Mostrar página inicial ao entrar no menu
        self.mostrar_pagina("home")

    # --------- helpers internos ---------

    def set_content(self, titulo: str, texto: str, links: list[tuple[str, str]] | None = None):
        """Actualiza o título, o texto e (opcionalmente) links clicáveis."""
        self.content_title.config(text=titulo)
        self.content_body.config(text=texto)

        # limpar links anteriores
        for child in self.links_frame.winfo_children():
            child.destroy()

        if links:
            ttk.Label(
                self.links_frame,
                text="Fontes externas:",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(0, 3))

            for label, url in links:
                link_lbl = ttk.Label(
                    self.links_frame,
                    text=f"• {label}",
                    foreground="#4ea3ff",
                    cursor="hand2",
                )
                link_lbl.pack(anchor="w")
                link_lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        # limpar também a zona dinâmica sempre que se muda de página
        for child in self.data_frame.winfo_children():
          child.destroy()

    def mostrar_pagina(self, pagina: str):
        """Páginas simples que só usam texto."""
        if pagina == "home":
            titulo = "Bem-vindo à Monitorização de NEOs"
            texto = (
                "Esta é a página inicial do sistema.\n\n"
                "A aplicação permite:\n"
                "  • Importar dados de asteroides a partir do ficheiro neo.csv;\n"
                "  • Consultar NEOs, PHAs e aproximações próximas;\n"
                "  • Ver e gerir alertas activos;\n"
                "  • Aceder a estatísticas e consultas gerais sobre a base de dados.\n\n"
                "Use o menu do lado esquerdo para navegar entre as diferentes áreas."
            )

            links = [
                ("Portal NEO da ESA", "https://neo.ssa.esa.int/"),
                ("NASA Eyes on Asteroids", "https://eyes.nasa.gov/apps/asteroids/#/home"),
                ("NASA/JPL Small-Body Database", "https://ssd.jpl.nasa.gov/tools/sb_ident.html#/"),
                ("Minor Planet Center - MPCORB.DAT", "https://minorplanetcenter.net/iau/info/MPCORB.DAT"),
                ("Kaggle - Prediction of Asteroid Diameter",
                 "https://www.kaggle.com/datasets/basu369victor/prediction-of-asteroid-diameter"),
            ]

        elif pagina == "insercao":
            titulo = "Aplicação de Inserção"
            texto = (
                "Nesta secção será possível:\n"
                "  • Seleccionar o ficheiro neo.csv fornecido pelo docente;\n"
                "  • Validar e importar os dados para as tabelas da base de dados;\n"
                "  • No futuro, editar registos e guardar alterações.\n\n"
                "Por agora esta página apresenta apenas a descrição da funcionalidade."
            )
            links = None

        elif pagina == "creditos":
            titulo = "Créditos"
            texto = (
                "Trabalho realizado por:\n"
                "  • Bernardete Coelho (a53654)\n"
                "  • Carlos Farinha (a53491)\n\n"
                "Unidade Curricular: Bases de Dados\n"
                "Licenciatura em Engenharia Informática\n"
                "Universidade da Beira Interior."
            )
            links = None

        else:
            titulo = "Página desconhecida"
            texto = "A página solicitada não está definida."
            links = None

        self.set_content(titulo, texto, links)

    # Helper para Treeviews
    def _fill_tree(self, tree: ttk.Treeview, cols, rows):
        tree["columns"] = cols
        tree["show"] = "headings"

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=100, stretch=True)

        for item in tree.get_children():
            tree.delete(item)

        for row in rows:
            tree.insert("", "end", values=[row[c] for c in cols])

    def _require_connection(self):
        """Verifica se existe ligação activa à BD (no controller)."""
        conn = getattr(self.controller, "db_conn", None)
        if conn is None:
            messagebox.showerror("Base de dados", "Não existe ligação activa à base de dados.")
            return None
        return conn

    # --------- PÁGINAS COM DADOS (Alertas / Monitorização / Consultas) ---------

    def show_alertas_page(self):
        conn = self._require_connection()
        if conn is None:
            return

        self.set_content(
            "Aplicação de Alertas",
            "Aqui são apresentados os alertas activos sobre aproximações "
            "próximas e outras situações críticas.\n\n"
            "A lista é obtida a partir da view vw_Alertas_Ativos_Detalhe e o "
            "resumo por nível usa a view vw_ResumoAlertasPorNivel."
        )

        frame = self.data_frame

        # Barra com botões
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 5))

        tree_alertas = ttk.Treeview(frame, height=10)
        tree_alertas.pack(fill="both", expand=True, pady=(5, 10))

        tree_resumo = ttk.Treeview(frame, height=4)
        tree_resumo.pack(fill="x", expand=False, pady=(2, 0))

        btn_atualizar = ttk.Button(
            toolbar,
            text="Atualizar lista de alertas",
            command=lambda: self._load_alertas(tree_alertas)
        )
        btn_atualizar.pack(side="left")

        btn_resumo = ttk.Button(
            toolbar,
            text="Mostrar resumo por nível",
            command=lambda: self._load_resumo_nivel(tree_resumo)
        )
        btn_resumo.pack(side="left", padx=(10, 0))

        # Carregar dados iniciais
        self._load_alertas(tree_alertas)
        self._load_resumo_nivel(tree_resumo)

    def _load_alertas(self, tree: ttk.Treeview):
        conn = self._require_connection()
        if conn is None:
            return
        cols, rows = consultas.fetch_alertas_ativos(conn)
        self._fill_tree(tree, cols, rows)

    def _load_resumo_nivel(self, tree: ttk.Treeview):
        conn = self._require_connection()
        if conn is None:
            return
        cols, rows = consultas.fetch_resumo_alertas_nivel(conn)
        self._fill_tree(tree, cols, rows)

    def show_monitorizacao_page(self):
        conn = self._require_connection()
        if conn is None:
            return

        self.set_content(
            "Aplicação de Monitorização",
            "Nesta secção são apresentadas algumas estatísticas e indicadores, "
            "baseados nas vistas de monitorização da base de dados."
        )

        frame = self.data_frame

        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True)

        # --- Tab 1: Ranking PHA ---
        tab_pha = ttk.Frame(notebook)
        notebook.add(tab_pha, text="Ranking PHAs")

        tree_pha = ttk.Treeview(tab_pha, height=12)
        tree_pha.pack(fill="both", expand=True, padx=5, pady=5)

        btn_pha = ttk.Button(
            tab_pha,
            text="Atualizar ranking",
            command=lambda: self._load_ranking_pha(tree_pha)
        )
        btn_pha.pack(anchor="e", padx=5, pady=(0, 5))

        # --- Tab 2: Centros mais activos ---
        tab_centros = ttk.Frame(notebook)
        notebook.add(tab_centros, text="Centros de observação")

        tree_centros = ttk.Treeview(tab_centros, height=12)
        tree_centros.pack(fill="both", expand=True, padx=5, pady=5)

        btn_centros = ttk.Button(
            tab_centros,
            text="Atualizar centros",
            command=lambda: self._load_centros_ativos(tree_centros)
        )
        btn_centros.pack(anchor="e", padx=5, pady=(0, 5))

        # --- Tab 3: Aproximações críticas ---
        tab_aprox = ttk.Frame(notebook)
        notebook.add(tab_aprox, text="Aprox. críticas")

        tree_aprox = ttk.Treeview(tab_aprox, height=12)
        tree_aprox.pack(fill="both", expand=True, padx=5, pady=5)

        btn_aprox = ttk.Button(
            tab_aprox,
            text="Atualizar aproximações",
            command=lambda: self._load_aproximacoes_criticas(tree_aprox)
        )
        btn_aprox.pack(anchor="e", padx=5, pady=(0, 5))

        # Carregar dados iniciais
        self._load_ranking_pha(tree_pha)
        self._load_centros_ativos(tree_centros)
        self._load_aproximacoes_criticas(tree_aprox)

    def _load_ranking_pha(self, tree: ttk.Treeview):
        conn = self._require_connection()
        if conn is None:
            return
        cols, rows = consultas.fetch_ranking_pha(conn, limite=15)
        self._fill_tree(tree, cols, rows)

    def _load_centros_ativos(self, tree: ttk.Treeview):
        conn = self._require_connection()
        if conn is None:
            return
        cols, rows = consultas.fetch_centros_com_mais_observacoes(conn, limite=15)
        self._fill_tree(tree, cols, rows)

    def _load_aproximacoes_criticas(self, tree: ttk.Treeview):
        conn = self._require_connection()
        if conn is None:
            return
        cols, rows = consultas.fetch_proximas_aproximacoes_criticas(conn, limite=30)
        self._fill_tree(tree, cols, rows)

    def show_consultas_page(self):
        conn = self._require_connection()
        if conn is None:
            return

        self.set_content(
            "Consultas gerais",
            "Nesta secção pode efectuar algumas consultas gerais à base de dados, "
            "usando vistas pré-definidas."
        )

        frame = self.data_frame

        # Mapear nomes amigáveis -> função de consulta
        self._consultas_map = {
            "Últimos asteroides detectados": consultas.fetch_ultimos_asteroides,
            "NEOs": consultas.fetch_asteroides_neo,
            "PHAs": consultas.fetch_asteroides_pha,
            "NEOs e PHAs": consultas.fetch_asteroides_neo_e_pha,
        }

        topo = ttk.Frame(frame)
        topo.pack(fill="x", pady=(0, 5))

        lbl = ttk.Label(topo, text="Escolha uma consulta:")
        lbl.pack(side="left")

        self._combo_consultas = ttk.Combobox(
            topo,
            values=list(self._consultas_map.keys()),
            state="readonly",
            width=35
        )
        self._combo_consultas.pack(side="left", padx=(5, 5))
        self._combo_consultas.current(0)

        btn_exec = ttk.Button(
            topo,
            text="Executar",
            command=self._executar_consulta_selecionada
        )
        btn_exec.pack(side="left")

        # Treeview para mostrar resultados
        self._tree_consultas = ttk.Treeview(frame, height=15)
        self._tree_consultas.pack(fill="both", expand=True, pady=(5, 0))

        # Executa a primeira por omissão
        self._executar_consulta_selecionada()

    def _executar_consulta_selecionada(self):
        conn = self._require_connection()
        if conn is None:
            return
        nome = self._combo_consultas.get()
        func = self._consultas_map.get(nome)
        if not func:
            messagebox.showwarning("Consultas", "Selecção de consulta inválida.")
            return
        cols, rows = func(conn)
        self._fill_tree(self._tree_consultas, cols, rows)

    # --------- handlers dos botões ---------

    def on_home(self):
        self.mostrar_pagina("home")

    def on_insercao(self):
        if not self.controller.db_conn:
            messagebox.showerror(
                "Base de dados",
                "Não existe ligação à base de dados. Configure primeiro a ligação."
            )
            return
        self.controller.show_frame("InsercaoESAFrame")

    def on_alertas(self):
        self.show_alertas_page()

    def on_monitorizacao(self):
        self.show_monitorizacao_page()

    def on_consultas(self):
        self.show_consultas_page()

    def on_user_config(self):
        self.controller.show_frame("UserConfigFrame")

    def on_creditos(self):
        self.mostrar_pagina("creditos")


class InsercaoESAFrame(ttk.Frame):
    """
    Frame para importar ficheiros CSV da ESA para a base de dados.
    """

    def __init__(self, parent, controller: "App"):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=20)

        ttk.Label(
            self,
            text="Importar dados da ESA",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 10))

        texto = (
            "Nesta secção pode importar os ficheiros CSV descarregados do site\n"
            "NEO da ESA para as tabelas auxiliares da base de dados:\n\n"
            "  • riskList.csv\n"
            "  • specialRiskList.csv\n"
            "  • pastImpactorsList.csv\n"
            "  • removedObjectsFromRiskList.csv\n"
            "  • upcomingClApp.csv\n"
            "  • searchResult.csv\n\n"
            "Também pode importar o ficheiro principal:\n"
            "  • neo.csv\n\n"
            "Cada botão abaixo deixa escolher o ficheiro e importa os dados para a BD."
        )

        ttk.Label(self, text=texto, justify="left", wraplength=600)\
            .pack(padx=20, pady=(0, 10))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="Importar riskList.csv",
            width=30,
            command=self.importar_risk,
        ).grid(row=0, column=0, padx=5, pady=3)

        ttk.Button(
            btn_frame,
            text="Importar specialRiskList.csv",
            width=30,
            command=self.importar_special_risk,
        ).grid(row=1, column=0, padx=5, pady=3)

        ttk.Button(
            btn_frame,
            text="Importar pastImpactorsList.csv",
            width=30,
            command=self.importar_past,
        ).grid(row=2, column=0, padx=5, pady=3)

        ttk.Button(
            btn_frame,
            text="Importar removedObjectsFromRiskList.csv",
            width=30,
            command=self.importar_removed,
        ).grid(row=3, column=0, padx=5, pady=3)

        ttk.Button(
            btn_frame,
            text="Importar upcomingClApp.csv",
            width=30,
            command=self.importar_upcoming,
        ).grid(row=4, column=0, padx=5, pady=3)

        ttk.Button(
            btn_frame,
            text="Importar searchResult.csv",
            width=30,
            command=self.importar_search,
        ).grid(row=5, column=0, padx=5, pady=3)

        ttk.Button(
            btn_frame,
            text="Importar neo.csv (asteroides base)",
            width=30,
            command=self.importar_neo,
        ).grid(row=6, column=0, padx=5, pady=(10, 3))

        ttk.Button(
            btn_frame,
            text="Importar MPCORB.DAT",
            width=30,
            command=self.importar_mpcorb,
        ).grid(row=7, column=0, padx=5, pady=3)

        ttk.Button(
            self,
            text="Voltar",
            command=lambda: self.controller.show_frame("MainMenuFrame"),
        ).pack(pady=15)

    # ---------- helpers internos ----------

    def _escolher_ficheiro(self, titulo_janela: str, nome_sugerido: str, filetypes=None) -> str | None:
        # se existir pasta docs, usar como directório inicial
        initialdir = os.path.join(os.getcwd(), "docs")
        if not os.path.isdir(initialdir):
            initialdir = os.getcwd()

        if filetypes is None:
            filetypes = [("Ficheiros CSV", "*.csv"), ("Todos os ficheiros", "*.*")]

        caminho = filedialog.askopenfilename(
            title=titulo_janela,
            initialdir=initialdir,
            filetypes=filetypes,
        )
        if not caminho:
            return None
        return caminho

    def _obter_conn(self) -> pyodbc.Connection | None:
        conn = self.controller.db_conn
        if conn is None:
            messagebox.showerror(
                "Base de dados",
                "Não existe ligação à base de dados. Volte ao menu e configure a ligação.",
            )
        return conn

    def _executar_import(self, func_import, titulo: str, nome_sugerido: str):
        conn = self._obter_conn()
        if conn is None:
            return

        caminho = self._escolher_ficheiro(titulo, nome_sugerido)
        if not caminho:
            return

        try:
            inseridos = func_import(conn, caminho)
        except Exception as exc:
            messagebox.showerror(
                "Erro na importação",
                f"Ocorreu um erro ao importar o ficheiro:\n{exc}",
            )
            return

        messagebox.showinfo(
            "Importação concluída",
            f"Foram inseridos {inseridos} registos a partir de:\n{caminho}",
        )

    # ---------- handlers de cada botão ----------

    def importar_neo(self):
        conn = self._obter_conn()
        if conn is None:
            return

        caminho = self._escolher_ficheiro("Selecionar neo.csv", "neo.csv")
        if not caminho:
            return

        try:
            inseridos = importar_neo_csv(conn, caminho)
        except Exception as exc:
            messagebox.showerror(
                "Erro na importação",
                f"Ocorreu um erro ao importar o ficheiro neo.csv:\n{exc}",
            )
            return

        messagebox.showinfo(
            "Importação concluída",
            f"Foram inseridos {inseridos} registos a partir de:\n{caminho}",
        )

    def importar_risk(self):
        self._executar_import(importar_risk_list, "Selecionar riskList.csv", "riskList.csv")

    def importar_special_risk(self):
        self._executar_import(importar_special_risk_list, "Selecionar specialRiskList.csv", "specialRiskList.csv")

    def importar_past(self):
        self._executar_import(importar_past_impactors, "Selecionar pastImpactorsList.csv", "pastImpactorsList.csv")

    def importar_removed(self):
        self._executar_import(importar_removed_from_risk, "Selecionar removedObjectsFromRiskList.csv", "removedObjectsFromRiskList.csv")

    def importar_upcoming(self):
        self._executar_import(importar_upcoming_cl_app, "Selecionar upcomingClApp.csv", "upcomingClApp.csv")

    def importar_search(self):
        self._executar_import(importar_search_result, "Selecionar searchResult.csv", "searchResult.csv")

    def importar_mpcorb(self):
        conn = self._obter_conn()
        if conn is None:
            return

        caminho = self._escolher_ficheiro(
            "Selecionar MPCORB.DAT", 
            "MPCORB.DAT",
            filetypes=[("Ficheiros MPCORB", "*.DAT"), ("Todos os ficheiros", "*.*")]
        )
        if not caminho:
            return

        try:
            inseridos = importar_mpcorb_dat(conn, caminho)
        except Exception as exc:
            messagebox.showerror(
                "Erro na importação",
                f"Ocorreu um erro ao importar o ficheiro MPCORB.DAT:\n{exc}",
            )
            return

        messagebox.showinfo(
            "Importação concluída",
            f"Foram processados {inseridos} registos a partir de:\n{caminho}",
        )


class UserConfigFrame(ttk.Frame):
    """
    Frame para gestão de utilizadores (alterar password, criar novos).
    """

    def __init__(self, parent, controller: "App"):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=20)

        ttk.Label(
            self,
            text="Configuração de Utilizador",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 20))

        # --- Alterar Meus Dados ---
        lbl_alterar = ttk.Label(self, text="Alterar Meus Dados", font=("Segoe UI", 12, "bold"))
        lbl_alterar.pack(anchor="w", pady=(0, 10))

        form_alterar = ttk.Frame(self)
        form_alterar.pack(fill="x", pady=(0, 20))

        ttk.Label(form_alterar, text="Novo Utilizador:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_new_user = ttk.Entry(form_alterar, width=25)
        self.entry_new_user.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_alterar, text="Nova Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_new_pass = ttk.Entry(form_alterar, show="*", width=25)
        self.entry_new_pass.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(form_alterar, text="Atualizar", command=self.on_update_me).grid(row=2, column=1, sticky="e", pady=10)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # --- Criar Novo Utilizador ---
        lbl_criar = ttk.Label(self, text="Criar Novo Utilizador", font=("Segoe UI", 12, "bold"))
        lbl_criar.pack(anchor="w", pady=(10, 10))

        form_criar = ttk.Frame(self)
        form_criar.pack(fill="x", pady=(0, 20))

        ttk.Label(form_criar, text="Utilizador:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_create_user = ttk.Entry(form_criar, width=25)
        self.entry_create_user.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_criar, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_create_pass = ttk.Entry(form_criar, show="*", width=25)
        self.entry_create_pass.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(form_criar, text="Criar", command=self.on_create_user).grid(row=2, column=1, sticky="e", pady=10)

        # Voltar
        ttk.Button(
            self,
            text="Voltar",
            command=lambda: self.controller.show_frame("MainMenuFrame"),
        ).pack(side="bottom", pady=20)

    def on_update_me(self):
        current_user = self.controller.admin_user
        if not current_user:
            messagebox.showerror("Erro", "Não há utilizador autenticado.")
            return

        new_user = self.entry_new_user.get().strip()
        new_pass = self.entry_new_pass.get()

        if not new_user or not new_pass:
            messagebox.showwarning("Dados em falta", "Preencha o novo utilizador e password.")
            return

        if alterar_credenciais(current_user, new_user, new_pass):
            messagebox.showinfo("Sucesso", "Dados atualizados com sucesso.")
            self.controller.set_admin_user(new_user)
            # Limpar campos
            self.entry_new_user.delete(0, tk.END)
            self.entry_new_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Não foi possível atualizar (o utilizador já existe?).")

    def on_create_user(self):
        user = self.entry_create_user.get().strip()
        pwd = self.entry_create_pass.get()

        if not user or not pwd:
            messagebox.showwarning("Dados em falta", "Preencha o utilizador e password.")
            return

        if criar_utilizador(user, pwd):
            messagebox.showinfo("Sucesso", f"Utilizador '{user}' criado com sucesso.")
            self.entry_create_user.delete(0, tk.END)
            self.entry_create_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Utilizador já existe.")



if __name__ == "__main__":
    app = App()
    app.mainloop()

