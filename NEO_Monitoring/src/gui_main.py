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

        self.title("NEO Monitor - Mission Control")
        self.geometry("1440x900")
        self.resizable(True, True)

        # Estado partilhado
        self.admin_user: str | None = None
        self.db_conn: pyodbc.Connection | None = None
        self.config = self.load_config()
        self.current_frame_name = "LoginFrame"
        self.current_frame = None

        # Carregar imagens
        self.load_images()

        # Canvas para fundo animado (Starfield)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#0b0d17")
        self.canvas.pack(fill="both", expand=True)

        self.bg_anim = BackgroundAnimation(self.canvas, 1440, 900)


        self.frames: dict[str, tk.Frame] = {}

        # Configurar estilos (Theme)
        self.style = ttk.Style(self)
        self.setup_theme()

        # Criar frames
        # Nota: A ordem de importação é importante se houver dependencias
        # Vamos redefinir as frames abaixo
        from tkinter import font
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Configure>", self.on_resize)

        for FrameClass in (LoginFrame, DbConfigFrame, MainMenuFrame, InsercaoESAFrame, UserConfigFrame, LoadingFrame):
             frame = FrameClass(parent=self, controller=self)
             self.frames[FrameClass.__name__] = frame

        self.show_frame("LoginFrame")




    def on_resize(self, event):
        if event.widget == self:
            w, h = event.width, event.height
            self.bg_anim.update_dimensions(w, h)
            self.update_card_position()

    def update_card_position(self):
        if not self.current_frame: return
        
        # Se for MainMenuFrame, ocupa quase tudo (menos a navbar se houver)
        # Se for Login/DbConfig, é um cartão centrado
        
        w = self.winfo_width()
        h = self.winfo_height()
        if w==1: w,h = 800,600

        self.canvas.delete("card_bg")
        
        try:
            if self.current_frame_name in ["LoginFrame", "DbConfigFrame", "LoadingFrame"]:
                # Cartão Centrado
                fw = self.current_frame.winfo_reqwidth()
                fh = self.current_frame.winfo_reqheight()
                card_w = fw + 40
                card_h = fh + 40
                x1 = (w - card_w) / 2
                y1 = (h - card_h) / 2
                x2 = x1 + card_w
                y2 = y1 + card_h
                
                create_rounded_rect(self.canvas, x1, y1, x2, y2, radius=15, fill="#15192b", outline="#00f0ff", width=1, tags="card_bg")
                self.canvas.create_window(w/2, h/2, window=self.current_frame, tags="current_frame", anchor="center")
            else:
                # Full Screen (com margens para o menu)
                self.canvas.create_window(0, 0, window=self.current_frame, tags="current_frame", anchor="nw", width=w, height=h)
        except Exception as e:
            print(f"CRITICAL ERROR in update_card_position: {e}")
            import traceback
            traceback.print_exc()


    def on_frame_configure(self, event):
        self.update_card_position()

    def load_images(self):
        self.img_logo_full = None
        self.img_logo_icon = None
        # (Manter código existente de load images)
        try:
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
            print(f"Erro assets: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: pass
        return {}

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f: json.dump(self.config, f)
        except: pass

    def setup_theme(self):
        self.style.theme_use("clam")
        

        # SPACE THEME PALETTE
        BG_DEEP     = "#0b0d17" # Fundo geral (Canvas)
        BG_CARD     = "#15192b" # Fundo cartões
        BG_INPUT    = "#1f243d" # Inputs
        ACCENT_CYAN = "#00f0ff" # Acentos Neon
        ACCENT_ROSE = "#ff005c" # Perigo/Importante
        TEXT_WHITE  = "#ffffff" # Texto principal (Brighter)
        TEXT_MUTED  = "#a0b0c5" # Texto secundário (Brighter)
        
        self.configure(bg=BG_DEEP)
        if hasattr(self, "canvas"):
            self.canvas.configure(bg=BG_DEEP)

        # Configurar Ttk Styles
        self.style.configure(".", background=BG_CARD, foreground=TEXT_WHITE, font=("Segoe UI", 10))
        self.style.configure("TFrame", background=BG_CARD)
        self.style.configure("TLabel", background=BG_CARD, foreground=TEXT_WHITE)
        
        # Botões Modernos
        self.style.configure("TButton", 
            background=BG_INPUT, 
            foreground=ACCENT_CYAN, 
            borderwidth=1, 
            focuscolor=ACCENT_CYAN,
            font=("Segoe UI", 10, "bold")
        )
        self.style.map("TButton", 
            background=[("active", "#252b45"), ("pressed", ACCENT_CYAN)],
            foreground=[("pressed", BG_DEEP)]
        )
        
        # Botões de Ação (Solid) - Criar classe custom 'Action.TButton' depois
        
        self.style.configure("TEntry", 
            fieldbackground=BG_INPUT, 
            foreground=TEXT_WHITE, 
            insertcolor=ACCENT_CYAN,
            borderwidth=0
        )
        
        self.style.configure("Treeview", 
            background="#1a1e33",
            fieldbackground="#1a1e33",
            foreground=TEXT_WHITE,
            rowheight=30,
            borderwidth=0
        )
        self.style.configure("Treeview.Heading", 
            background="#252b45", 
            foreground=ACCENT_CYAN, 
            font=("Segoe UI", 10, "bold")
        )
        self.style.map("Treeview", background=[("selected", "#2a3b55")], foreground=[("selected", ACCENT_CYAN)])
        
        # Notebook (Tabs)
        self.style.configure("TNotebook", background=BG_DEEP, borderwidth=0)
        self.style.configure("TNotebook.Tab", 
            background=BG_CARD, 
            foreground=TEXT_MUTED, 
            padding=[15, 5], 
            font=("Segoe UI", 10)
        )
        self.style.map("TNotebook.Tab", 
            background=[("selected", ACCENT_CYAN)], 
            foreground=[("selected", BG_DEEP)]
        )

    def show_frame(self, name: str):
        print(f"DEBUG: show_frame calling {name}")
        if self.current_frame:
            self.current_frame.unbind("<Configure>")
        
        self.current_frame_name = name
        self.current_frame = self.frames[name]
        self.current_frame.tkraise()
        
        self.update_card_position()
        self.current_frame.bind("<Configure>", self.on_frame_configure)

    def update_card_position(self):
        # print("DEBUG: update_card_position called") # too verbose if called on resize
        if not self.current_frame: return
        
        # Se for MainMenuFrame, ocupa quase tudo (menos a navbar se houver)
        # Se for Login/DbConfig, é um cartão centrado
        
        w = self.winfo_width()
        h = self.winfo_height()
        if w==1: w,h = 800,600

        self.canvas.delete("card_bg")
        
        if self.current_frame_name in ["LoginFrame", "DbConfigFrame", "LoadingFrame"]:
            # Cartão Centrado
            fw = self.current_frame.winfo_reqwidth()
            fh = self.current_frame.winfo_reqheight()
            card_w = fw + 40
            card_h = fh + 40
            x1 = (w - card_w) / 2
            y1 = (h - card_h) / 2
            x2 = x1 + card_w
            y2 = y1 + card_h
            
            create_rounded_rect(self.canvas, x1, y1, x2, y2, radius=15, fill="#15192b", outline="#00f0ff", width=1, tags="card_bg")

            self.canvas.create_window(w/2, h/2, window=self.current_frame, tags="current_frame", anchor="center")
        else:
            # Full Screen (com margens para o menu)
            # O MainMenuFrame vai gerir o seu layout interno (Top Bar + Content)
            # Nós só colocamos o frame a encher o ecrã
            self.canvas.create_window(0, 0, window=self.current_frame, tags="current_frame", anchor="nw", width=w, height=h)

        if hasattr(self.current_frame, "refresh_data"):
             self.current_frame.refresh_data()

    def set_admin_user(self, user):
        self.admin_user = user

    def set_db_connection(self, conn):
        self.db_conn = conn
        self.depois_de_ligar_bd()

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



class LoadingFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#15192b")
        # self.configure(padding=40)
        
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


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        
        
        
        # Imagem Logo Full
        if self.controller.img_logo_full:
             lbl_img = tk.Label(self, image=self.controller.img_logo_full, bg="#15192b")
             lbl_img.grid(row=0, column=0, pady=(0, 20))

        tk.Label(self, text="Login de administrador", font=("Segoe UI", 16, "bold"), bg="#15192b", fg="#e0e6ed").grid(row=1, column=0, pady=(0, 20))
        tk.Label(self, text="Introduza as credenciais de administrador.", font=("Segoe UI", 10), bg="#15192b", fg="#e0e6ed").grid(row=2, column=0, pady=(0, 20))

        form = tk.Frame(self, bg="#15192b")
        form.grid(row=3, column=0, pady=10)

        tk.Label(form, text="Utilizador:", bg="#15192b", fg="#e0e6ed").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_user = tk.Entry(form, width=25, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_user.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Palavra-passe:", bg="#15192b", fg="#e0e6ed").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_pass = tk.Entry(form, show="*", width=25, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_pass.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Bind Enter key
        self.entry_user.bind("<Return>", lambda e: self.on_login())
        self.entry_pass.bind("<Return>", lambda e: self.on_login())

        self.save_login_var = tk.BooleanVar()
        tk.Checkbutton(form, text="Guardar dados", variable=self.save_login_var, bg="#15192b", fg="#e0e6ed", selectcolor="#15192b", activebackground="#15192b", activeforeground="#e0e6ed").grid(row=2, column=0, columnspan=2, pady=5)

        # Botão Custom Style (simulado com tk.Button)
        btn = tk.Button(self, text="ENTRAR", command=self.on_login, bg="#1f243d", fg="#00f0ff", font=("Segoe UI", 10, "bold"), activebackground="#00f0ff", activeforeground="#1f243d", relief="flat", padx=20, pady=5)
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





class DbConfigFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#15192b")
        # self.configure(padding=20)

        # Carregar defaults ou config
        cfg = self.controller.config.get("db", {})
        
        self.servidor_var = tk.StringVar(value=cfg.get("server", "localhost\\SQLEXPRESS"))
        self.base_dados_var = tk.StringVar(value=cfg.get("database", "BD_PL2_09"))
        self.auth_mode_var = tk.StringVar(value=cfg.get("auth_mode", "windows"))
        self.user_var = tk.StringVar(value=cfg.get("user", ""))
        self.pass_var = tk.StringVar(value=cfg.get("password", ""))
        self.ip_var = tk.StringVar(value=cfg.get("ip", "localhost"))
        self.port_var = tk.StringVar(value=cfg.get("port", "1433"))

        tk.Label(self, text="Ligação à base de dados", font=("Segoe UI", 16, "bold"), bg="#15192b", fg="#e0e6ed").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Grid para o formulário
        self.form = tk.Frame(self, bg="#15192b")
        self.form.grid(row=1, column=0)

        row = 0
        self.lbl_servidor = tk.Label(self.form, text="Servidor:", bg="#15192b", fg="#e0e6ed")
        self.lbl_servidor.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        self.entry_servidor = tk.Entry(self.form, textvariable=self.servidor_var, width=30, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_servidor.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        # Campos IP e Porta (inicialmente ocultos ou não, dependendo do modo)
        self.lbl_ip = tk.Label(self.form, text="IP:", bg="#15192b", fg="#e0e6ed")
        self.lbl_ip.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        self.entry_ip = tk.Entry(self.form, textvariable=self.ip_var, width=20, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_ip.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        row += 1
        self.lbl_port = tk.Label(self.form, text="Porta:", bg="#15192b", fg="#e0e6ed")
        self.lbl_port.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        self.entry_port = tk.Entry(self.form, textvariable=self.port_var, width=10, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_port.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        row += 1
        tk.Label(self.form, text="Base de dados:", bg="#15192b", fg="#e0e6ed").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        tk.Entry(self.form, textvariable=self.base_dados_var, width=30, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat").grid(
            row=row, column=1, sticky="w", padx=10, pady=5
        )

        row += 1
        tk.Label(self.form, text="Autenticação:", bg="#15192b", fg="#e0e6ed").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        
        auth_frame = tk.Frame(self.form, bg="#15192b")
        auth_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        tk.Radiobutton(
            auth_frame,
            text="Windows",
            variable=self.auth_mode_var,
            value="windows",
            command=self.on_auth_mode_change,
            bg="#15192b", fg="#e0e6ed", selectcolor="#15192b", activebackground="#15192b", activeforeground="#e0e6ed"
        ).pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(
            auth_frame,
            text="SQL Server",
            variable=self.auth_mode_var,
            value="sql",
            command=self.on_auth_mode_change,
            bg="#15192b", fg="#e0e6ed", selectcolor="#15192b", activebackground="#15192b", activeforeground="#e0e6ed"
        ).pack(side="left")

        # Widgets de user/pass (guardamos referências para esconder/mostrar)
        row += 1
        self.lbl_user_bd = tk.Label(self.form, text="Utilizador BD:", bg="#15192b", fg="#e0e6ed")
        self.lbl_user_bd.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        
        self.entry_user_bd = tk.Entry(self.form, textvariable=self.user_var, width=25, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_user_bd.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        row += 1
        self.lbl_pass_bd = tk.Label(self.form, text="Palavra-passe BD:", bg="#15192b", fg="#e0e6ed")
        self.lbl_pass_bd.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        
        self.entry_pass_bd = tk.Entry(self.form, textvariable=self.pass_var, show="*", width=25, bg="#1f243d", fg="#e0e6ed", insertbackground="#00f0ff", relief="flat")
        self.entry_pass_bd.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        # Botões
        btn_frame = tk.Frame(self, bg="#15192b")
        btn_frame.grid(row=2, column=0, pady=20)

        tk.Button(btn_frame, text="VOLTAR", command=self.on_back, bg="#1f243d", fg="#e0e6ed", relief="flat", padx=15, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text="TESTAR LIGAÇÃO", command=self.on_testar_ligacao, bg="#1f243d", fg="#00f0ff", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=5).pack(side="left", padx=5)

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


class MainMenuFrame(tk.Frame):
    """
    Main Shell for the logged-in experience.
    Contains the Top Navigation Bar and a Content Area.
    """
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#0b0d17")
        
        # Grid layout: Row 0 = Navbar, Row 1 = Content
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Top Nav Bar ---
        self.navbar = ttk.Frame(self, style="TFrame")
        self.navbar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Logo/Title Area
        lbl_brand = ttk.Label(self.navbar, text="🚀 NEO MISSION CONTROL", font=("Segoe UI", 12, "bold"), foreground="#00f0ff")
        lbl_brand.pack(side="left", padx=20, pady=10)
        
        # Navigation Buttons
        self.nav_btns_frame = ttk.Frame(self.navbar)
        self.nav_btns_frame.pack(side="left", padx=40)
        
        self.create_nav_btn("Dashboard", "dashboard")
        self.create_nav_btn("Pesquisa", "search")
        self.create_nav_btn("Inserção (Wizard)", "wizard")
        self.create_nav_btn("Alertas", "alertas")
        self.create_nav_btn("Monitorização", "monitor")
        
        # User / Actions Area
        user_frame = ttk.Frame(self.navbar)
        user_frame.pack(side="right", padx=20)
        
        self.lbl_user = ttk.Label(user_frame, text="Commander", font=("Segoe UI", 10))
        self.lbl_user.pack(side="left", padx=10)
        
        btn_logout = ttk.Button(user_frame, text="LOGOUT", command=self.on_logout, width=8)
        btn_logout.pack(side="left")

        # --- Main Content Area ---
        self.content_area = ttk.Frame(self)
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Dictionary of sub-frames
        self.sub_frames = {}
        for F in (DashboardFrame, SearchFrame, WizardFrame):
            page_name = F.__name__
            frame = F(parent=self.content_area, controller=self.controller)
            self.sub_frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure content area grid
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(0, weight=1)
        
        self.current_sub_frame = None
        self.show_sub_frame("DashboardFrame")

    def create_nav_btn(self, text, code):
        btn = ttk.Button(self.nav_btns_frame, text=text, command=lambda c=code: self.navigate_to(c))
        btn.pack(side="left", padx=5)

    def navigate_to(self, code):
        if code == "dashboard": self.show_sub_frame("DashboardFrame")
        elif code == "search": self.show_sub_frame("SearchFrame")
        elif code == "wizard": self.show_sub_frame("WizardFrame")
        elif code == "alertas": 
             # For legacy pages, we still use the old show_frame method if possible, 
             # OR we should migrate them to be subframes.
             # For now, let's keep them accessible via the controller if they exist as MainFrames,
             # BUT here we are inside MainMenuFrame. 
             # Ideally we should refrain from switching the ROOT frame unless necessary.
             # Let's placeholder this:
             messagebox.showinfo("Em construção", "A secção de Alertas está a ser migrada.")
        elif code == "monitor": 
             messagebox.showinfo("Em construção", "A secção de Monitorização está a ser migrada.")

    def show_sub_frame(self, name):
        if name in self.sub_frames:
            frame = self.sub_frames[name]
            frame.tkraise()
            self.current_sub_frame = frame
            # Refresh data if needed
            if hasattr(frame, 'refresh_data'):
                frame.refresh_data()

    def on_logout(self):
        self.controller.show_frame("LoginFrame")

    def refresh_data(self):
        try:
             if self.current_sub_frame and hasattr(self.current_sub_frame, "refresh_data"):
                  self.current_sub_frame.refresh_data()
        except Exception as e:
             print(f"Erro no MainMenuFrame.refresh_data: {e}")


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        self.lbl_welcome = ttk.Label(self, text="Vision General", font=("Segoe UI", 16, "bold"))
        self.lbl_welcome.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))
        
        self.card_neos = self.create_kpi_card(0, "Total NEOs", "0")
        self.card_pha = self.create_kpi_card(1, "PHAs Identificados", "0", color="#ff005c")
        self.card_alerts = self.create_kpi_card(2, "Alertas Ativos", "0", color="#ffbe0b")
        
        lbl_recent = ttk.Label(self, text="Atividade Recente", font=("Segoe UI", 12, "bold"))
        lbl_recent.grid(row=2, column=0, sticky="w", pady=(20, 10))
        
        cols = ("Nome", "Diametro", "H_Mag", "Obs")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

    def create_kpi_card(self, col, title, value, color="#00f0ff"):
        frame = ttk.Frame(self, style="TFrame")
        frame.grid(row=1, column=col, sticky="ew", padx=10)
        
        lbl_title = ttk.Label(frame, text=title.upper(), foreground="#8b9bb4", font=("Segoe UI", 9))
        lbl_title.pack(anchor="w")
        
        lbl_val = ttk.Label(frame, text=value, foreground=color, font=("Segoe UI", 24, "bold"))
        lbl_val.pack(anchor="w")
        return lbl_val

    def refresh_data(self):
        conn = self.controller.db_conn
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Asteroide WHERE flag_neo=1")
            neo_count = cur.fetchone()[0]
            self.card_neos.config(text=str(neo_count))
            
            cur.execute("SELECT COUNT(*) FROM Asteroide WHERE flag_pha=1")
            pha_count = cur.fetchone()[0]
            self.card_pha.config(text=str(pha_count))
            
            cur.execute("SELECT COUNT(*) FROM Alerta WHERE ativo=1")
            alert_count = cur.fetchone()[0]
            self.card_alerts.config(text=str(alert_count))
            cur.close()
            
            cols, rows = consultas.fetch_ultimos_asteroides(conn)
            self.tree.delete(*self.tree.get_children())
            for r in rows:
                self.tree.insert("", "end", values=(
                    r.get('nome_completo', 'N/A'), 
                    r.get('diametro_km', 'N/A'), 
                    r.get('H_mag', 'N/A'), 
                    f"ID: {r.get('id_asteroide')}"
                ))
        except Exception as e:
            print(f"Erro no dashboard: {e}")


class SearchFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        filters_frame = ttk.Frame(self)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(filters_frame, text="Nome/Desig:").pack(side="left", padx=5)
        self.ent_name = ttk.Entry(filters_frame, width=15)
        self.ent_name.pack(side="left", padx=5)
        
        ttk.Label(filters_frame, text="Perigo:").pack(side="left", padx=5)
        self.cb_danger = ttk.Combobox(filters_frame, values=["Todos", "NEO", "PHA"], state="readonly", width=10)
        self.cb_danger.current(0)
        self.cb_danger.pack(side="left", padx=5)
        
        ttk.Label(filters_frame, text="Ordenar:").pack(side="left", padx=5)
        self.cb_sort = ttk.Combobox(filters_frame, values=["Nome", "Tamanho (Maior)", "Tamanho (Menor)", "Perigo (Mais próximo)"], state="readonly", width=15)
        self.cb_sort.current(0)
        self.cb_sort.pack(side="left", padx=5)
        
        btn_search = ttk.Button(filters_frame, text="🔍 Pesquisar", command=lambda: self.do_search(reset_page=True))
        btn_search.pack(side="left", padx=10)
        
        self.ent_name.bind("<KeyRelease>", lambda e: self.do_search(reset_page=True))
        self.cb_danger.bind("<<ComboboxSelected>>", lambda e: self.do_search(reset_page=True))
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.do_search(reset_page=True))
        
        # Initial search
        self.do_search()
        
        cols = ("ID", "Nome", "Diametro (km)", "H (mag)", "MOID (au)", "NEO", "PHA")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("ID", width=50)
        self.tree.pack(fill="both", expand=True)
        
        self.tree.tag_configure("dangerous", foreground="#ff005c")
        self.tree.tag_configure("warning", foreground="#ffbe0b")

        # Paginação Controls
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill="x", pady=10)

        self.btn_prev_page = ttk.Button(nav_frame, text="< Página Anterior", command=self.prev_page, state="disabled")
        self.btn_prev_page.pack(side="left", padx=10)

        self.lbl_page = ttk.Label(nav_frame, text="Página 1")
        self.lbl_page.pack(side="left", padx=10)

        self.btn_next_page = ttk.Button(nav_frame, text="Próxima Página >", command=self.next_page)
        self.btn_next_page.pack(side="left", padx=10)

        self.current_page = 1
        self.page_size = 50

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.do_search()

    def next_page(self):
        self.current_page += 1
        self.do_search()

    def do_search(self, reset_page=False):
        try:
            if reset_page:
                self.current_page = 1

            conn = self.controller.db_conn
            if not conn: return
            
            name = self.ent_name.get().strip()
            danger = self.cb_danger.get()
            sort_by = self.cb_sort.get()
            
            cols, rows = consultas.fetch_filtered_asteroids(
                conn, 
                name=name, 
                danger_level=danger, 
                sort_by=sort_by,
                page=self.current_page,
                page_size=self.page_size
            )
            
            self.tree.delete(*self.tree.get_children())
            
            if not rows:
                 self.lbl_page.config(text=f"Página {self.current_page} (Sem resultados)")
            else:
                 self.lbl_page.config(text=f"Página {self.current_page}")

            # Update buttons state
            if self.current_page == 1:
                self.btn_prev_page.config(state="disabled")
            else:
                self.btn_prev_page.config(state="normal")
            
            if len(rows) < self.page_size:
                self.btn_next_page.config(state="disabled")
            else:
                self.btn_next_page.config(state="normal")


            for r in rows:
                tag = ""
                if r['flag_pha'] == 1: tag = "dangerous"
                elif r['flag_neo'] == 1: tag = "warning"
                
                self.tree.insert("", "end", values=(
                    r.get('id_asteroide', 'N/A'), 
                    r.get('nome_completo', 'N/A'), 
                    r.get('diametro_km') if r.get('diametro_km') is not None else "N/A", 
                    r.get('H_mag') if r.get('H_mag') is not None else "N/A", 
                    r.get('moid_ua') if r.get('moid_ua') is not None else "N/A", 
                    "SIM" if r.get('flag_neo') else "", 
                    "SIM" if r.get('flag_pha') else ""
                ), tags=(tag,))
        except Exception as e:
            print(f"Erro no SearchFrame.do_search: {e}")
            import traceback
            traceback.print_exc()
            



class WizardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.steps = ["1. Contexto", "2. Asteroide", "3. Observação"]
        self.current_step = 0
        
        self.lbl_step = ttk.Label(self, text=self.steps[0], font=("Segoe UI", 12, "bold"), foreground="#00f0ff")
        self.lbl_step.pack(pady=10)
        
        self.step_frame = ttk.Frame(self)
        self.step_frame.pack(fill="both", expand=True, padx=50)
        
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(pady=20)
        
        self.btn_prev = ttk.Button(self.nav_frame, text="< Anterior", command=self.prev_step, state="disabled")
        self.btn_prev.pack(side="left", padx=10)
        
        self.btn_next = ttk.Button(self.nav_frame, text="Próximo >", command=self.next_step)
        self.btn_next.pack(side="left", padx=10)
        
        self.vars = {
            "centro_cod": tk.StringVar(),
            "centro_nome": tk.StringVar(),
            "centro_pais": tk.StringVar(),
            "equip_nome": tk.StringVar(),
            "equip_tipo": tk.StringVar(),
            "astro_nome": tk.StringVar(),
            "soft_nome": tk.StringVar(),
            "ast_pdes": tk.StringVar(),
            "ast_nome": tk.StringVar(),
            "ast_neo": tk.BooleanVar(),
            "ast_pha": tk.BooleanVar(),
            "ast_h": tk.DoubleVar(value=0.0),
            "obs_data": tk.StringVar(value="2025-01-01 12:00:00"),
            "obs_modo": tk.StringVar(value="MANUAL"),
            "obs_notas": tk.StringVar()
        }
        
        self.render_step_1()

    def clear_frame(self):
        for widget in self.step_frame.winfo_children():
            widget.destroy()

    def render_step_1(self):
        self.clear_frame()
        f = self.step_frame
        
        ttk.Label(f, text="Centro Observação (Código/Nome/País)").grid(row=0, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["centro_cod"], width=10).grid(row=0, column=1)
        ttk.Entry(f, textvariable=self.vars["centro_nome"], width=30).grid(row=0, column=2)
        ttk.Entry(f, textvariable=self.vars["centro_pais"], width=15).grid(row=0, column=3)
        
        ttk.Label(f, text="Equipamento (Nome/Tipo)").grid(row=1, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["equip_nome"], width=30).grid(row=1, column=1, columnspan=2, sticky="ew")
        ttk.Entry(f, textvariable=self.vars["equip_tipo"], width=15).grid(row=1, column=3)
        
        ttk.Label(f, text="Astrónomo").grid(row=2, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["astro_nome"], width=40).grid(row=2, column=1, columnspan=3, sticky="w")
        
        ttk.Label(f, text="Software").grid(row=3, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["soft_nome"], width=40).grid(row=3, column=1, columnspan=3, sticky="w")

    def render_step_2(self):
        self.clear_frame()
        f = self.step_frame
        
        ttk.Label(f, text="Designação (PDES)").grid(row=0, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["ast_pdes"]).grid(row=0, column=1, sticky="w")
        
        ttk.Label(f, text="Nome Completo").grid(row=1, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["ast_nome"]).grid(row=1, column=1, sticky="w")
        
        ttk.Label(f, text="Magnitude (H)").grid(row=2, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["ast_h"]).grid(row=2, column=1, sticky="w")
        
        ttk.Checkbutton(f, text="É NEO?", variable=self.vars["ast_neo"]).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(f, text="É PHA?", variable=self.vars["ast_pha"]).grid(row=4, column=1, sticky="w")

    def render_step_3(self):
        self.clear_frame()
        f = self.step_frame
        
        ttk.Label(f, text="Data/Hora Observação (YYYY-MM-DD HH:MM:SS)").grid(row=0, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["obs_data"], width=25).grid(row=0, column=1, sticky="w")
        
        ttk.Label(f, text="Modo").grid(row=1, column=0, pady=5, sticky="e")
        ttk.Combobox(f, textvariable=self.vars["obs_modo"], values=["MANUAL", "CCD", "VISUAL"]).grid(row=1, column=1, sticky="w")
        
        ttk.Label(f, text="Notas").grid(row=2, column=0, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.vars["obs_notas"], width=50).grid(row=2, column=1, sticky="w")

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_ui()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_ui()
        else:
            self.submit()

    def update_ui(self):
        self.lbl_step.config(text=self.steps[self.current_step])
        self.btn_prev.config(state="normal" if self.current_step > 0 else "disabled")
        self.btn_next.config(text="Submeter" if self.current_step == len(self.steps) - 1 else "Próximo >")
        
        if self.current_step == 0: self.render_step_1()
        elif self.current_step == 1: self.render_step_2()
        elif self.current_step == 2: self.render_step_3()

    def submit(self):
        conn = self.controller.db_conn
        if not conn: return
        try:
            from services.insercao import manual_insert_full_record
            manual_insert_full_record(
                conn,
                self.vars["centro_cod"].get(), self.vars["centro_nome"].get(), self.vars["centro_pais"].get(),
                self.vars["equip_nome"].get(), self.vars["equip_tipo"].get(),
                self.vars["astro_nome"].get(),
                self.vars["soft_nome"].get(),
                self.vars["ast_pdes"].get(), self.vars["ast_nome"].get(), 
                self.vars["ast_neo"].get(), self.vars["ast_pha"].get(), self.vars["ast_h"].get(),
                self.vars["obs_data"].get(), self.vars["obs_modo"].get(), self.vars["obs_notas"].get()
            )
            messagebox.showinfo("Sucesso", "Dados inseridos com sucesso!")
            self.current_step = 0
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Erro", str(e))


class InsercaoESAFrame(tk.Frame):
    """
    Frame para importar ficheiros CSV da ESA para a base de dados.
    """

    def __init__(self, parent, controller: "App"):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#15192b")
        # self.configure(padding=20)

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


class UserConfigFrame(tk.Frame):
    """
    Frame para gestão de utilizadores (alterar password, criar novos).
    """

    def __init__(self, parent, controller: "App"):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#15192b")
        # self.configure(padding=20)

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

