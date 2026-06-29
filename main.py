import csv
import os
import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp 
from kivy.properties import ListProperty
from kivy.utils import platform

# Ajuste de teclado virtual
Window.softinput_mode = 'below_target'

# --- PALETA DE CORES DE ALTA VISIBILIDADE ---
BG_COLOR = (0.95, 0.96, 0.98, 1)      
TEXT_MAIN = (0, 0, 0, 1)              
TEXT_MUTED = (0.25, 0.30, 0.35, 1)    
PRIMARY_GREEN = (0.05, 0.60, 0.40, 1) 
ACCENT_BLUE = (0.05, 0.45, 0.75, 1)    
SLATE_GRAY = (0.40, 0.45, 0.50, 1)    
DANGER_RED = (0.85, 0.15, 0.15, 1)    

INPUT_HEIGHT = dp(58)
BUTTON_HEIGHT_LARGE = dp(68)
BUTTON_HEIGHT_MEDIUM = dp(58)
FONT_SIZE_LARGE = dp(22)
FONT_SIZE_MEDIUM = dp(18)

# --- GERENCIAMENTO DINÂMICO DE CAMINHOS (COMPATÍVEL COM ANDROID 14) ---
def get_db_path():
    if platform == 'android':
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        return os.path.join(context.getFilesDir().getAbsolutePath(), "inventario.db")
    return "inventario.db"

def get_export_path(filename):
    if platform == 'android':
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        ext_dir = os.path.join(context.getExternalFilesDir(None).getAbsolutePath(), "InventarioFlorestal")
        if not os.path.exists(ext_dir):
            os.makedirs(ext_dir)
        return os.path.join(ext_dir, filename)
    return filename

def init_db():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS arvores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            timestamp TEXT,
            gps TEXT,
            placa TEXT,
            nome TEXT,
            altura TEXT,
            caps TEXT,
            FOREIGN KEY(projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# ------------------- COMPONENTES CUSTOMIZADOS -------------------

class SmoothButton(Button):
    base_color = ListProperty([0.6, 0.6, 0.6, 1])
    def __init__(self, bg_color=(0.6, 0.6, 0.6, 1), text_color=(1, 1, 1, 1), radius=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.base_color = bg_color
        self.color = text_color
        self.radius = radius or [dp(12)]
        self.bold = True
        with self.canvas.before:
            self.canvas_color = Color(*self.base_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._update_state)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_state(self, instance, value):
        if value == 'down':
            self.canvas_color.rgba = [c * 0.85 for c in self.base_color[:3]] + [self.base_color[3] if len(self.base_color) > 3 else 1]
        else:
            self.canvas_color.rgba = self.base_color

    def on_base_color(self, instance, value):
        if hasattr(self, 'canvas_color'):
            self.canvas_color.rgba = value

class SmoothTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = PRIMARY_GREEN
        self.foreground_color = (0, 0, 0, 1)         
        self.hint_text_color = (0.40, 0.45, 0.50, 1)  
        self.font_size = dp(18)                                      
        self.padding = [dp(14), dp(16), dp(14), dp(12)] 
        self.multiline = False
        with self.canvas.before:
            Color(1, 1, 1, 1)  
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(0.70, 0.75, 0.80, 1)  
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)), width=dp(1.5))
        self.bind(pos=self._update_rect, size=self._update_rect)
        
    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.border_line.rounded_rectangle = (instance.x, instance.y, instance.width, instance.height, dp(12))

# ------------------- TELAS DO APLICATIVO -------------------

class ProjectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_screen_bg, pos=self._update_screen_bg)
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(20))
        main_layout.add_widget(Label(text="Inventário Florestal", font_size=dp(26), bold=True, color=TEXT_MAIN, size_hint_y=None, height=dp(45)))
        
        novo_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(140))
        self.project_input = SmoothTextInput(hint_text="Nome do novo empreendimento", size_hint_y=None, height=INPUT_HEIGHT)
        btn_criar = SmoothButton(text="Criar Novo Projeto", bg_color=PRIMARY_GREEN, size_hint_y=None, height=BUTTON_HEIGHT_MEDIUM)
        btn_criar.bind(on_press=self.criar_projeto)
        novo_box.add_widget(self.project_input)
        novo_box.add_widget(btn_criar)
        main_layout.add_widget(novo_box)
        
        main_layout.add_widget(Label(text="Projetos Salvos (SQLite)", font_size=dp(16), bold=True, color=TEXT_MUTED, size_hint_y=None, height=dp(25)))
        
        scroll = ScrollView(size_hint=(1, 1))
        self.projects_list_layout = GridLayout(cols=1, spacing=dp(10), padding=dp(2), size_hint_y=None)
        self.projects_list_layout.bind(minimum_height=self.projects_list_layout.setter('height'))
        scroll.add_widget(self.projects_list_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)

    def _update_screen_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_pre_enter(self):
        self.carregar_projetos()

    def criar_projeto(self, instance):
        nome = self.project_input.text.strip()
        if not nome:
            return
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projetos (nome, data_criacao) VALUES (?, ?)", (nome, datetime.now().strftime('%d/%m/%Y %H:%M')))
        proj_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.project_input.text = ""
        self.abrir_projeto(proj_id, nome)

    def carregar_projetos(self):
        self.projects_list_layout.clear_widgets()
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, data_criacao FROM projetos ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        for pid, nome, data in rows:
            row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(70), padding=[dp(10), dp(8), dp(10), dp(8)])
            with row.canvas.before:
                Color(1, 1, 1, 1)
                row.bg_card = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(10)])
            row.bind(pos=lambda ins, val: setattr(ins.bg_card, 'pos', val), size=lambda ins, val: setattr(ins.bg_card, 'size', val))
            
            lbl = Label(text=f"{nome}\n[color=748596]{data}[/color]", markup=True, font_size=dp(14), color=TEXT_MAIN, size_hint_x=0.46, halign='left', valign='middle')
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], val[1])))
            row.add_widget(lbl)
            
            btn_abrir = SmoothButton(text="Abrir", bg_color=PRIMARY_GREEN, size_hint_x=0.18, font_size=dp(13), radius=[dp(8)])
            btn_abrir.bind(on_press=lambda b, i=pid, n=nome: self.abrir_projeto(i, n))
            row.add_widget(btn_abrir)

            btn_editar = SmoothButton(text="Editar", bg_color=ACCENT_BLUE, size_hint_x=0.18, font_size=dp(13), radius=[dp(8)])
            btn_editar.bind(on_press=lambda b, i=pid, n=nome: self.editar_projeto(i, n))
            row.add_widget(btn_editar)
            
            btn_deletar = SmoothButton(text="Excluir", bg_color=DANGER_RED, size_hint_x=0.18, font_size=dp(13), radius=[dp(8)])
            btn_deletar.bind(on_press=lambda b, i=pid: self.confirmar_exclusao(i))
            row.add_widget(btn_deletar)
            
            self.projects_list_layout.add_widget(row)

    def abrir_projeto(self, proj_id, nome):
        app = App.get_running_app()
        app.current_project_id = proj_id
        app.current_project_name = nome
        app.sm.current = "trees"

    def editar_projeto(self, proj_id, nome_atual):
        box = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        box.add_widget(Label(text="Alterar nome do empreendimento:", font_size=dp(16), color=(1, 1, 1, 1)))
        
        txt_input = SmoothTextInput(text=nome_atual, size_hint_y=None, height=INPUT_HEIGHT)
        box.add_widget(txt_input)
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        btn_salvar = SmoothButton(text="Salvar", bg_color=PRIMARY_GREEN)
        btn_cancelar = SmoothButton(text="Cancelar", bg_color=SLATE_GRAY)
        btn_box.add_widget(btn_salvar)
        btn_box.add_widget(btn_cancelar)
        box.add_widget(btn_box)
        
        popup = Popup(title="Editar Nome do Projeto", content=box, size_hint=(0.9, 0.35))
        
        def salvar_nome(instance):
            novo_nome = txt_input.text.strip()
            if novo_nome:
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()
                cursor.execute("UPDATE projetos SET nome=? WHERE id=?", (novo_nome, proj_id))
                conn.commit()
                conn.close()
                popup.dismiss()
                self.carregar_projetos()
                
        btn_salvar.bind(on_press=salvar_nome)
        btn_cancelar.bind(on_press=popup.dismiss)
        popup.open()

    def confirmar_exclusao(self, proj_id):
        box = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        box.add_widget(Label(text="Tem certeza que deseja apagar o projeto?\nEsta ação é irreversível.", halign="center", font_size=dp(16)))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        btn_sim = SmoothButton(text="Sim, Apagar", bg_color=DANGER_RED)
        btn_nao = SmoothButton(text="Cancelar", bg_color=SLATE_GRAY)
        
        btn_box.add_widget(btn_sim)
        btn_box.add_widget(btn_nao)
        box.add_widget(btn_box)
        
        popup = Popup(title="Aviso de Exclusão", content=box, size_hint=(0.85, 0.35))
        
        def deletar(instance):
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projetos WHERE id=?", (proj_id,))
            cursor.execute("DELETE FROM arvores WHERE projeto_id=?", (proj_id,))
            conn.commit()
            conn.close()
            popup.dismiss()
            self.carregar_projetos()
            
        btn_sim.bind(on_press=deletar)
        btn_nao.bind(on_press=popup.dismiss)
        popup.open()


class TreeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editing_id = None
        
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_screen_bg, pos=self._update_screen_bg)
        
        root_layout = BoxLayout(orientation='vertical')
        
        top_bar = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(95), padding=[dp(20), dp(10), dp(20), dp(5)], spacing=dp(5))
        btn_voltar = SmoothButton(text="< Voltar para Projetos", bg_color=SLATE_GRAY, size_hint_y=None, height=dp(45))
        btn_voltar.bind(on_press=self.go_back)
        self.lbl_titulo = Label(text="Nova Árvore", font_size=FONT_SIZE_LARGE, bold=True, color=TEXT_MAIN, size_hint_y=None, height=dp(35), halign='left')
        self.lbl_titulo.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], val[1])))
        top_bar.add_widget(btn_voltar)
        top_bar.add_widget(self.lbl_titulo)
        root_layout.add_widget(top_bar)

        scroll = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(orientation='vertical', spacing=dp(16), padding=[dp(20), dp(5), dp(20), dp(10)], size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.gps_input = SmoothTextInput(hint_text="Identificação GPS", size_hint=(1,None), height=INPUT_HEIGHT)
        self.placa_input = SmoothTextInput(text="1", hint_text="Número da placa", size_hint=(1,None), height=INPUT_HEIGHT)
        self.name_input = SmoothTextInput(hint_text="Nome comum / Científico", size_hint=(1,None), height=INPUT_HEIGHT)
        self.height_input = SmoothTextInput(hint_text="Altura da árvore (m)", size_hint=(1,None), height=INPUT_HEIGHT, input_type='number', input_filter='float')

        for w in [self.gps_input, self.placa_input, self.name_input, self.height_input]:
            self.layout.add_widget(w)

        self.layout.add_widget(Label(text="Medições de Fustes / CAP (cm)", font_size=FONT_SIZE_MEDIUM, bold=True, color=TEXT_MAIN, size_hint_y=None, height=dp(30)))
        
        self.caps_inputs = []
        self.caps_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.caps_box.bind(minimum_height=self.caps_box.setter('height'))
        self.layout.add_widget(self.caps_box)

        self.add_cap_field(None)

        self.add_cap_button = SmoothButton(text="+ Incluir outro Fuste/CAP", bg_color=SLATE_GRAY, size_hint_y=None, height=dp(55))
        self.add_cap_button.bind(on_press=self.add_cap_field)
        self.layout.add_widget(self.add_cap_button)

        self.add_tree_button = SmoothButton(text="Adicionar Árvore", bg_color=PRIMARY_GREEN, size_hint_y=None, height=BUTTON_HEIGHT_LARGE)
        self.add_tree_button.bind(on_press=self.save_tree)
        self.layout.add_widget(self.add_tree_button)

        self.layout.add_widget(Label(text="Últimas Coletas do Projeto", font_size=dp(16), bold=True, color=TEXT_MUTED, size_hint_y=None, height=dp(30)))

        self.tree_list_layout = GridLayout(cols=1, spacing=dp(10), padding=dp(2), size_hint_y=None)
        self.tree_list_layout.bind(minimum_height=self.tree_list_layout.setter('height'))
        self.layout.add_widget(self.tree_list_layout)
        
        scroll.add_widget(self.layout)
        root_layout.add_widget(scroll)

        bottom_bar = BoxLayout(orientation='horizontal', spacing=dp(12), padding=dp(15), size_hint_y=None, height=dp(85))
        with bottom_bar.canvas.before:
            Color(0.90, 0.92, 0.95, 1)
            bottom_bar.bb_rect = Rectangle(pos=bottom_bar.pos, size=bottom_bar.size)
        bottom_bar.bind(pos=lambda ins, val: setattr(ins.bb_rect, 'pos', val), size=lambda ins, val: setattr(ins.bb_rect, 'size', val))

        self.history_button = SmoothButton(text="Ver Histórico", bg_color=ACCENT_BLUE, size_hint_x=0.5, font_size=dp(16))
        self.history_button.bind(on_press=lambda x: setattr(App.get_running_app().sm, 'current', 'history'))
        
        self.export_button = SmoothButton(text="Finalizar e Exportar", bg_color=PRIMARY_GREEN, size_hint_x=0.5, font_size=dp(16))
        self.export_button.bind(on_press=lambda x: setattr(App.get_running_app().sm, 'current', 'confirm'))
        
        bottom_bar.add_widget(self.history_button)
        bottom_bar.add_widget(self.export_button)
        root_layout.add_widget(bottom_bar)

        self.add_widget(root_layout)

    def _update_screen_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def go_back(self, instance):
        App.get_running_app().sm.current = "project"

    def on_pre_enter(self):
        app = App.get_running_app()
        self.lbl_titulo.text = f"Projeto: {app.current_project_name}"
        self.update_tree_list_ui()
        self.proxima_placa()

    def add_cap_field(self, instance, initial_text=""):
        row_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=INPUT_HEIGHT)
        cap_input = SmoothTextInput(text=initial_text, hint_text="CAP (cm)", size_hint_x=0.80, input_type='number', input_filter='float')
        self.caps_inputs.append(cap_input)
        
        remove_button = SmoothButton(text="X", bg_color=DANGER_RED, size_hint_x=0.20, radius=[dp(12)])
        remove_button.bind(on_press=lambda btn: self.remove_cap_field(row_layout, cap_input))
        
        row_layout.add_widget(cap_input)
        row_layout.add_widget(remove_button)
        self.caps_box.add_widget(row_layout)

    def remove_cap_field(self, row_layout, cap_input):
        if cap_input in self.caps_inputs:
            self.caps_inputs.remove(cap_input)
        self.caps_box.remove_widget(row_layout)

    def proxima_placa(self):
        app = App.get_running_app()
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT placa FROM arvores WHERE projeto_id=?", (app.current_project_id,))
        placas = cursor.fetchall()
        conn.close()
        
        max_p = 0
        for p in placas:
            try:
                ip = int(p[0])
                if ip > max_p: max_p = ip
            except ValueError: pass
        self.placa_input.text = str(max_p + 1)

    def save_tree(self, instance):
        gps = self.gps_input.text.strip()
        placa = self.placa_input.text.strip()
        name = self.name_input.text.strip()
        height = self.height_input.text.strip()
        caps_list = [cap.text.strip() for cap in self.caps_inputs if cap.text.strip()]
        caps = ",".join(caps_list)

        vazios = []
        if not gps: vazios.append("GPS")
        if not placa: vazios.append("Placa")
        if not name: vazios.append("Nome da Espécie")
        if not height: vazios.append("Altura")
        if not caps_list: vazios.append("CAP/Fuste")

        if vazios:
            box = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
            campos_str = ", ".join(vazios)
            
            lbl_aviso = Label(
                text=f"Atenção! Os seguintes campos estão vazios:\n[color=ff6b6b]{campos_str}[/color]\n\nDeseja salvar o registro assim mesmo?",
                markup=True, halign="center", font_size=dp(16), color=(1, 1, 1, 1)
            )
            box.add_widget(lbl_aviso)
            
            btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
            btn_confirmar = SmoothButton(text="Salvar Assim Mesmo", bg_color=PRIMARY_GREEN)
            btn_ajustar = SmoothButton(text="Voltar e Ajustar", bg_color=SLATE_GRAY)
            
            btn_box.add_widget(btn_confirmar)
            btn_box.add_widget(btn_ajustar)
            box.add_widget(btn_box)
            
            popup = Popup(title="Campos Incompletos", content=box, size_hint=(0.9, 0.38))
            
            btn_confirmar.bind(on_press=lambda b: [popup.dismiss(), self.execute_save(gps, placa, name, height, caps)])
            btn_ajustar.bind(on_press=popup.dismiss)
            popup.open()
        else:
            self.execute_save(gps, placa, name, height, caps)

    def execute_save(self, gps, placa, name, height, caps):
        app = App.get_running_app()
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        if self.editing_id is not None:
            cursor.execute('''
                UPDATE arvores SET gps=?, placa=?, nome=?, altura=?, caps=? WHERE id=?
            ''', (gps, placa, name, height, caps, self.editing_id))
            self.editing_id = None
            self.add_tree_button.text = "Adicionar Árvore"
            self.add_tree_button.base_color = PRIMARY_GREEN
        else:
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO arvores (projeto_id, timestamp, gps, placa, nome, altura, caps)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (app.current_project_id, now_str, gps, placa, name, height, caps))

        conn.commit()
        conn.close()

        self.gps_input.text = ""
        self.name_input.text = ""
        self.height_input.text = ""
        self.caps_box.clear_widgets()
        self.caps_inputs.clear()
        self.add_cap_field(None)
        
        self.update_tree_list_ui()
        self.proxima_placa()

    def update_tree_list_ui(self):
        self.tree_list_layout.clear_widgets()
        app = App.get_running_app()
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        # CORREÇÃO: Corrigido o nome do campo de project_id para projeto_id para alinhar com o SQLite
        cursor.execute("SELECT id, gps, placa, nome, altura, caps FROM arvores WHERE projeto_id=? ORDER BY id DESC LIMIT 5", (app.current_project_id,))
        rows = cursor.fetchall()
        conn.close()

        for tid, gps, placa, nome, alt, caps in rows:
            row_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(75), padding=[dp(15), dp(10), dp(15), dp(10)])
            with row_layout.canvas.before:
                Color(1, 1, 1, 1) 
                row_layout.bg_card = RoundedRectangle(pos=row_layout.pos, size=row_layout.size, radius=[dp(12)])
            row_layout.bind(pos=lambda ins, val: setattr(ins.bg_card, 'pos', val), size=lambda ins, val: setattr(ins.bg_card, 'size', val))
            
            txt_nome = nome if nome else "Sem nome"
            txt_gps = gps if gps else "-"
            txt_caps = caps if caps else "-"
            texto_linha = f"Placa: {placa} | {txt_nome} (H: {alt}m)\nGPS: {txt_gps} | CAP: {txt_caps}"
            
            lbl = Label(text=texto_linha, font_size=dp(13), color=TEXT_MAIN, size_hint_x=0.55, halign='left', valign='middle')
            lbl.bind(size=lambda instance, val: setattr(instance, 'text_size', (val[0], val[1])))
            row_layout.add_widget(lbl)
            
            edit_btn = SmoothButton(text="Editar", bg_color=ACCENT_BLUE, size_hint_x=0.22, font_size=dp(14), radius=[dp(8)])
            edit_btn.bind(on_press=lambda btn, i=tid: self.edit_tree(i))
            row_layout.add_widget(edit_btn)
            
            del_btn = SmoothButton(text="Excluir", bg_color=DANGER_RED, size_hint_x=0.23, font_size=dp(14), radius=[dp(8)])
            del_btn.bind(on_press=lambda btn, i=tid: self.delete_tree(i))
            row_layout.add_widget(del_btn)
            
            self.tree_list_layout.add_widget(row_layout)

    def edit_tree(self, tree_id):
        self.editing_id = tree_id
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT gps, placa, nome, altura, caps FROM arvores WHERE id=?", (tree_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            self.gps_input.text = row[0]
            self.placa_input.text = row[1]
            self.name_input.text = row[2]
            self.height_input.text = row[3]
            
            self.caps_box.clear_widgets()
            self.caps_inputs.clear()
            
            if row[4]:
                for cap_val in row[4].split(","):
                    self.add_cap_field(None, initial_text=cap_val)
            else:
                self.add_cap_field(None)

            self.add_tree_button.text = "Salvar Alterações"
            self.add_tree_button.base_color = ACCENT_BLUE

    def delete_tree(self, tree_id):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM arvores WHERE id=?", (tree_id,))
        conn.commit()
        conn.close()
        self.update_tree_list_ui()
        self.proxima_placa()


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_screen_bg, pos=self._update_screen_bg)
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        main_layout.add_widget(Label(text="Histórico do Projeto", font_size=dp(24), bold=True, color=TEXT_MAIN, size_hint_y=None, height=dp(50)))

        scroll = ScrollView(size_hint=(1, 1))
        self.history_list_layout = GridLayout(cols=1, spacing=dp(10), padding=dp(2), size_hint_y=None)
        self.history_list_layout.bind(minimum_height=self.history_list_layout.setter('height'))
        scroll.add_widget(self.history_list_layout)
        main_layout.add_widget(scroll)

        back_button = SmoothButton(text="< Voltar à Coleta", bg_color=SLATE_GRAY, size_hint_y=None, height=BUTTON_HEIGHT_MEDIUM)
        back_button.bind(on_press=self.go_back)
        main_layout.add_widget(back_button)
        self.add_widget(main_layout)

    def _update_screen_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def go_back(self, instance):
        App.get_running_app().sm.current = "trees"

    def on_pre_enter(self):
        self.update_history_list_ui()

    def update_history_list_ui(self):
        self.history_list_layout.clear_widgets()
        app = App.get_running_app()
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, gps, placa, nome, altura, caps FROM arvores WHERE projeto_id=? ORDER BY id DESC", (app.current_project_id,))
        rows = cursor.fetchall()
        conn.close()
        
        tree_screen = app.sm.get_screen("trees")

        for tid, gps, placa, nome, alt, caps in rows:
            row_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(75), padding=[dp(15), dp(10), dp(15), dp(10)])
            with row_layout.canvas.before:
                Color(1, 1, 1, 1)
                row_layout.bg_card = RoundedRectangle(pos=row_layout.pos, size=row_layout.size, radius=[dp(12)])
            row_layout.bind(pos=lambda ins, val: setattr(ins.bg_card, 'pos', val), size=lambda ins, val: setattr(ins.bg_card, 'size', val))
            
            txt_gps = gps if gps else "-"
            txt_nome = nome if nome else "Sem nome"
            # CORREÇÃO DEFINITIVA: Operador ternário perfeitamente formatado sem ':' no meio da expressão
            txt_caps = caps if caps else "-"
            texto_linha = f"Placa: {placa} | {txt_nome} (H: {alt}m)\nGPS: {txt_gps} | CAP: {txt_caps}"
            
            lbl = Label(text=texto_linha, font_size=dp(13), color=TEXT_MAIN, size_hint_x=0.55, halign='left', valign='middle')
            lbl.bind(size=lambda instance, val: setattr(instance, 'text_size', (val[0], val[1])))
            row_layout.add_widget(lbl)
            
            edit_btn = SmoothButton(text="Editar", bg_color=ACCENT_BLUE, size_hint_x=0.22, font_size=dp(14), radius=[dp(8)])
            edit_btn.bind(on_press=lambda btn, i=tid: self.edit_and_go(tree_screen, i))
            row_layout.add_widget(edit_btn)
            
            del_btn = SmoothButton(text="Excluir", bg_color=DANGER_RED, size_hint_x=0.23, font_size=dp(14), radius=[dp(8)])
            del_btn.bind(on_press=lambda btn, i=tid: self.delete_from_history(i))
            row_layout.add_widget(del_btn)
            
            self.history_list_layout.add_widget(row_layout)

    def edit_and_go(self, tree_screen, tree_id):
        tree_screen.edit_tree(tree_id)
        App.get_running_app().sm.current = "trees"

    def delete_from_history(self, tree_id):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM arvores WHERE id=?", (tree_id,))
        conn.commit()
        conn.close()
        self.update_history_list_ui()

class ConfirmScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_screen_bg, pos=self._update_screen_bg)
        
        self.main_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(25))
        self.label = Label(text="", font_size=FONT_SIZE_LARGE, bold=True, color=TEXT_MAIN, size_hint_y=None, height=dp(50))
        self.main_layout.add_widget(self.label)

        scroll = ScrollView(size_hint=(1, 1))
        self.preview_list_layout = GridLayout(cols=1, spacing=dp(10), padding=dp(2), size_hint_y=None)
        self.preview_list_layout.bind(minimum_height=self.preview_list_layout.setter('height'))
        scroll.add_widget(self.preview_list_layout)
        self.main_layout.add_widget(scroll)

        buttons_layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(150))
        
        export_button = SmoothButton(text="Exportar para CSV", bg_color=PRIMARY_GREEN, size_hint_y=None, height=BUTTON_HEIGHT_MEDIUM)
        export_button.bind(on_press=self.exportar_csv)
        buttons_layout.add_widget(export_button)

        cancel_button = SmoothButton(text="Voltar para a Coleta", bg_color=SLATE_GRAY, size_hint_y=None, height=BUTTON_HEIGHT_MEDIUM)
        cancel_button.bind(on_press=self.cancel_save)
        buttons_layout.add_widget(cancel_button)

        self.main_layout.add_widget(buttons_layout)
        self.add_widget(self.main_layout)

    def _update_screen_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_pre_enter(self):
        app = App.get_running_app()
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT placa, nome, altura, gps FROM arvores WHERE projeto_id=?", (app.current_project_id,))
        rows = cursor.fetchall()
        conn.close()

        self.label.text = f"Resumo: {len(rows)} Árvores Cadastradas"
        self.preview_list_layout.clear_widgets()

        for placa, nome, altura, gps in rows:
            row_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(65), padding=[dp(15), dp(10), dp(15), dp(10)])
            with row_layout.canvas.before:
                Color(1, 1, 1, 1)
                row_layout.bg_card = RoundedRectangle(pos=row_layout.pos, size=row_layout.size, radius=[dp(10)])
            row_layout.bind(pos=lambda ins, val: setattr(ins.bg_card, 'pos', val), size=lambda ins, val: setattr(ins.bg_card, 'size', val))
            
            n = nome if nome else "Não identificado"
            h = f"{altura}m" if altura else "-"
            g = gps if gps else "-"
            texto_resumo = f"Placa: {placa}  |  {n}  |  H: {h}  |  GPS: {g}"
            
            lbl = Label(text=texto_resumo, font_size=dp(14), color=TEXT_MAIN, halign='left', valign='middle')
            lbl.bind(size=lambda instance, val: setattr(instance, 'text_size', (val[0], val[1])))
            row_layout.add_widget(lbl)
            self.preview_list_layout.add_widget(row_layout)

    def exportar_csv(self, instance):
        app = App.get_running_app()
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, gps, placa, nome, altura, caps FROM arvores WHERE projeto_id=?", (app.current_project_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return

        max_caps = 0
        parsed_rows = []
        for r in rows:
            timestamp, gps, placa, nome, altura, caps_str = r
            caps_list = caps_str.split(",") if caps_str else []
            if len(caps_list) > max_caps:
                max_caps = len(caps_list)
            parsed_rows.append([timestamp, gps, placa, nome, altura] + caps_list)

        header = ["Data_Hora", "GPS", "Placa", "Nome", "Altura"] + [f"CAP{i+1}" for i in range(max_caps)]
        raw_filename = f"{app.current_project_name}_exportado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Caminho temporário local interno do app
        if platform == 'android':
            from jnius import autoclass
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            temp_filepath = os.path.join(context.getFilesDir().getAbsolutePath(), raw_filename)
        else:
            temp_filepath = raw_filename

        # Escreve o CSV localmente primeiro
        with open(temp_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(header)
            for row in parsed_rows:
                while len(row) < len(header):
                    row.append("")
                writer.writerow(row)

        # Move o arquivo para a pasta pública "Documentos/InventarioFlorestal"
        caminho_final_msg = temp_filepath
        if platform == 'android':
            try:
                from jnius import autoclass
                context = autoclass('org.kivy.android.PythonActivity').mActivity
                resolver = context.getContentResolver()
                
                ContentValues = autoclass('android.content.ContentValues')
                String = autoclass('java.lang.String')
                Environment = autoclass('android.os.Environment')
                
                # CORREÇÃO AQUI: Importando a classe interna VERSION do Android corretamente
                BuildVersion = autoclass('android.os.Build$VERSION')
                MediaColumns = autoclass('android.provider.MediaStore$MediaColumns')
                
                values = ContentValues()
                values.put(MediaColumns.DISPLAY_NAME, String(raw_filename))
                values.put(MediaColumns.MIME_TYPE, String("text/csv"))
                
                if BuildVersion.SDK_INT >= 29:  # Android 10 ou superior (Scoped Storage)
                    values.put(MediaColumns.RELATIVE_PATH, String(Environment.DIRECTORY_DOCUMENTS + "/InventarioFlorestal"))
                    
                    MediaStoreFiles = autoclass('android.provider.MediaStore$Files')
                    collection = MediaStoreFiles.getContentUri("external")
                    
                    uri = resolver.insert(collection, values)
                    
                    if uri:
                        out_stream = resolver.openOutputStream(uri)
                        with open(temp_filepath, 'r', encoding='utf-8') as f:
                            csv_text = f.read()
                        j_string = String(csv_text)
                        out_stream.write(j_string.getBytes(String("UTF-8")))
                        out_stream.close()
                        caminho_final_msg = f"Memória Interna > Documentos > InventarioFlorestal > {raw_filename}"
                        
                        try: os.remove(temp_filepath)
                        except: pass
                else:  # Fallback para Android 9 ou inferior
                    pub_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath()
                    target_dir = os.path.join(pub_dir, "InventarioFlorestal")
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    target_path = os.path.join(target_dir, raw_filename)
                    import shutil
                    shutil.copy(temp_filepath, target_path)
                    caminho_final_msg = target_path
            except Exception as e:
                caminho_final_msg = f"Salvo no armazenamento interno do App: {temp_filepath}\nErro: {str(e)}"

        # Exibe o popup com o caminho atualizado para a pasta de Documentos
        box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        box.add_widget(Label(text=f"Arquivo gerado com sucesso!\n\nDisponível em:\n[color=0df2a1]{caminho_final_msg}[/color]", halign="center", font_size=dp(14), markup=True))
        btn = SmoothButton(text="Ok", bg_color=PRIMARY_GREEN, size_hint_y=None, height=dp(50))
        box.add_widget(btn)
        popup = Popup(title="Exportação Concluída", content=box, size_hint=(0.9, 0.45))
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def cancel_save(self, instance):
        App.get_running_app().sm.current = "trees"
        
class TreeApp(App):
    def build(self):
        init_db()  
        self.current_project_id = None
        self.current_project_name = ""
        self.sm = ScreenManager()
        self.sm.add_widget(ProjectScreen(name="project"))
        self.sm.add_widget(TreeScreen(name="trees"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(ConfirmScreen(name="confirm"))
        return self.sm

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET])

if __name__ == '__main__':
    TreeApp().run()
