import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.lang import Builder

# --- ESTILOS VISUAIS ---
PRIMARY_GREEN = get_color_from_hex("#2E7D32")
SECONDARY_GREEN = get_color_from_hex("#4CAF50")
LIGHT_BG = get_color_from_hex("#F5F5F5")
TEXT_DARK = get_color_from_hex("#212121")
ALERT_RED = get_color_from_hex("#C62828")

Builder.load_string('''
<LinhaHistorico>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(65)
    padding: dp(8)
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: (0.8, 0.8, 0.8, 1)
        Line:
            points: [self.x, self.y, self.x + self.width, self.y]
            width: 1
    BoxLayout:
        Label:
            text: self.parent.parent.text_placa
            bold: True
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.3
        Label:
            text: self.parent.parent.text_nome
            bold: True
            color: 0.18, 0.49, 0.2, 1
            size_hint_x: 0.7
    Label:
        text: self.parent.text_detalhes
        font_size: '12sp'
        color: 0.4, 0.4, 0.4, 1

<TelaMenu>:
    canvas.before:
        Color:
            rgba: 0.96, 0.96, 0.96, 1
        Rectangle: size: self.size, pos: self.pos
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)
        
        Label:
            text: "INVENTÁRIO FLORESTAL"
            font_size: '24sp'
            bold: True
            color: 0.18, 0.49, 0.2, 1
            size_hint_y: None
            height: dp(60)

        BoxLayout:
            orientation: 'vertical'
            spacing: dp(5)
            size_hint_y: None
            height: dp(100)
            Label:
                text: "Novo Levantamento (Nome do Projeto/Fazenda):"
                color: TEXT_DARK
                halign: 'left'
                text_size: self.width, None
            TextInput:
                id: input_novo_projeto
                multiline: False
                hint_text: "Ex: Fazenda_Cedro_Talhao_01"
            Button:
                text: "INICIAR NOVO TRABALHO"
                background_color: PRIMARY_GREEN
                on_release: root.criar_novo_projeto()

        Label:
            text: "Ou continue um trabalho existente:"
            color: TEXT_DARK
            size_hint_y: None
            height: dp(30)
            
        ScrollView:
            GridLayout:
                id: container_projetos
                cols: 1
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

<TelaCadastro>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color: rgba: 0.96, 0.96, 0.96, 1
            Rectangle: size: self.size, pos: self.pos
            
        Label:
            id: lbl_projeto_ativo
            text: "Projeto: ---"
            background_color: 0.2, 0.2, 0.2, 1
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(40)
            canvas.before:
                Color: rgba: 0.2, 0.2, 0.2, 1
                Rectangle: size: self.size, pos: self.pos

        ScrollView:
            GridLayout:
                id: container_caps
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(12)

                BoxLayout:
                    size_hint_y: None
                    height: dp(45)
                    Label:
                        text: "Nº Placa *:"
                        color: TEXT_DARK
                        size_hint_x: 0.4
                    TextInput:
                        id: input_placa
                        multiline: False
                
                BoxLayout:
                    size_hint_y: None
                    height: dp(45)
                    Label:
                        text: "Espécie *:"
                        color: TEXT_DARK
                        size_hint_x: 0.4
                    TextInput:
                        id: input_nome
                        multiline: False

                BoxLayout:
                    size_hint_y: None
                    height: dp(45)
                    Label:
                        text: "CAP Fuste 1 (cm):"
                        color: TEXT_DARK
                        size_hint_x: 0.4
                    TextInput:
                        id: input_cap1
                        input_type: 'number'
                        input_filter: 'float'

                Button:
                    text: "+ Adicionar Fuste Extra"
                    size_hint_y: None
                    height: dp(40)
                    background_color: SECONDARY_GREEN
                    on_release: root.incluir_novo_fuste()

                BoxLayout:
                    size_hint_y: None
                    height: dp(45)
                    Label:
                        text: "Altura Tot. (m):"
                        color: TEXT_DARK
                        size_hint_x: 0.4
                    TextInput:
                        id: input_altura
                        input_type: 'number'
                        input_filter: 'float'

                BoxLayout:
                    size_hint_y: None
                    height: dp(45)
                    Label:
                        text: "Nº Ponto GPS:"
                        color: TEXT_DARK
                        size_hint_x: 0.4
                    TextInput:
                        id: input_gps
                        input_type: 'number'
                        input_filter: 'int'

                Button:
                    text: "SALVAR ÁRVORE"
                    size_hint_y: None
                    height: dp(60)
                    background_color: PRIMARY_GREEN
                    bold: True
                    on_release: root.validar_e_salvar()

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(5)
            spacing: dp(10)
            Button:
                text: "Menu Inicial"
                background_color: 0.4, 0.4, 0.4, 1
                on_release: root.manager.current = 'menu'
            Button:
                text: "Histórico / Busca"
                background_color: SECONDARY_GREEN
                on_release: root.manager.current = 'historico'

<TelaHistorico>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        TextInput:
            id: txt_pesquisa
            hint_text: "Pesquisar por Placa ou Nome..."
            size_hint_y: None
            height: dp(45)
            on_text: root.carregar_dados_rv(self.text)
        RecycleView:
            id: rv_historico
            viewclass: 'LinhaHistorico'
            RecycleBoxLayout:
                default_size: None, dp(65)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
        Button:
            text: "Voltar ao Cadastro"
            size_hint_y: None
            height: dp(50)
            on_release: root.manager.current = 'cadastro'
''')

# --- BANCO DE DADOS ---
def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('inventario_florestal.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

def init_db():
    db_query('''CREATE TABLE IF NOT EXISTS levantamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT, projeto TEXT, placa TEXT, 
        nome TEXT, caps TEXT, altura TEXT, gps TEXT)''')

# --- TELAS ---
class TelaMenu(Screen):
    def on_enter(self):
        init_db()
        self.atualizar_lista_projetos()

    def atualizar_lista_projetos(self):
        self.ids.container_projetos.clear_widgets()
        projetos = db_query("SELECT DISTINCT projeto FROM levantamento", fetch=True)
        for p in projetos:
            nome_p = p[0]
            btn = Button(text=f"Abrir: {nome_p}", size_hint_y=None, height=dp(50), background_color=SECONDARY_GREEN)
            btn.bind(on_release=lambda x, n=nome_p: self.abrir_projeto(n))
            self.ids.container_projetos.add_widget(btn)

    def criar_novo_projeto(self):
        nome = self.ids.input_novo_projeto.text.strip()
        if nome:
            self.abrir_projeto(nome)

    def abrir_projeto(self, nome):
        App.get_running_app().projeto_ativo = nome
        self.manager.current = 'cadastro'

class LinhaHistorico(RecycleDataViewBehavior, BoxLayout):
    text_placa = StringProperty(""); text_nome = StringProperty(""); text_detalhes = StringProperty("")
    def refresh_view_attrs(self, rv, index, data):
        self.text_placa = f"P: {data['placa']}"; self.text_nome = data['nome']
        self.text_detalhes = f"CAPs: {data['caps']} | H: {data['altura']} | GPS: {data['gps']}"
        return super().refresh_view_attrs(rv, index, data)

class TelaCadastro(Screen):
    cap_inputs = ListProperty([])
    def on_enter(self):
        self.projeto_atual = App.get_running_app().projeto_ativo
        self.ids.lbl_projeto_ativo.text = f"Projeto Ativo: {self.projeto_atual}"
        self.atualizar_placa()

    def atualizar_placa(self):
        res = db_query("SELECT MAX(CAST(placa AS INTEGER)) FROM levantamento WHERE projeto=?", (self.projeto_atual,), fetch=True)
        prox = (res[0][0] + 1) if res and res[0][0] is not None else 1
        self.ids.input_placa.text = str(prox)

    def incluir_novo_fuste(self):
        box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        box.add_widget(Label(text=f"CAP F{len(self.cap_inputs)+2}:", color=TEXT_DARK, size_hint_x=0.4))
        txt = TextInput(input_type='number', input_filter='float')
        box.add_widget(txt); self.ids.container_caps.add_widget(box)
        self.cap_inputs.append(txt)

    def validar_e_salvar(self):
        p, n, h, g = self.ids.input_placa.text.strip(), self.ids.input_nome.text.strip(), self.ids.input_altura.text.strip(), self.ids.input_gps.text.strip()
        caps = [self.ids.input_cap1.text.strip()] + [ti.text.strip() for ti in self.cap_inputs]
        caps_f = ", ".join([v for v in caps if v])

        if not p or not n:
            return self.popup_msg("Placa e Espécie são obrigatórios!", ALERT_RED)

        avisos = []
        if not caps_f: avisos.append("- Sem CAP")
        if not h: avisos.append("- Sem Altura")
        if not g: avisos.append("- Sem GPS")
        
        dup_p = db_query("SELECT 1 FROM levantamento WHERE projeto=? AND placa=?", (self.projeto_atual, p), fetch=True)
        if dup_p: avisos.append(f"- Placa {p} já existe")

        if avisos:
            msg = "Avisos:\\n" + "\\n".join(avisos) + "\\n\\nSalvar assim mesmo?"
            self.popup_confirm(msg, p, n, caps_f, h, g)
        else:
            self.salvar(p, n, caps_f, h, g)

    def popup_msg(self, txt, cor):
        p = Popup(title="Aviso", content=Label(text=txt), size_hint=(0.8, 0.3))
        p.open()

    def popup_confirm(self, txt, p_val, n_val, c_val, h_val, g_val):
        cont = BoxLayout(orientation='vertical', padding=10, spacing=10)
        cont.add_widget(Label(text=txt))
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        b1 = Button(text="Corrigir", background_color=PRIMARY_GREEN)
        b2 = Button(text="Salvar", background_color=ALERT_RED)
        btns.add_widget(b1); btns.add_widget(b2); cont.add_widget(btns)
        pop = Popup(title="Atenção", content=cont, size_hint=(0.9, 0.5))
        b1.bind(on_release=pop.dismiss)
        b2.bind(on_release=lambda x: [self.salvar(p_val, n_val, c_val, h_val, g_val), pop.dismiss()])
        pop.open()

    def salvar(self, p, n, c, h, g):
        db_query("INSERT INTO levantamento (projeto, placa, nome, caps, altura, gps) VALUES (?,?,?,?,?,?)", (self.projeto_atual, p, n, c, h, g))
        self.ids.input_nome.text = ""; self.ids.input_cap1.text = ""; self.ids.input_altura.text = ""; self.ids.input_gps.text = ""
        for ti in self.cap_inputs: self.ids.container_caps.remove_widget(ti.parent)
        self.cap_inputs.clear(); self.atualizar_placa()

class TelaHistorico(Screen):
    def on_enter(self):
        self.proj = App.get_running_app().projeto_ativo
        self.carregar_dados_rv()
    def carregar_dados_rv(self, busca=""):
        q = "SELECT placa, nome, caps, altura, gps FROM levantamento WHERE projeto=? AND (placa LIKE ? OR nome LIKE ?) ORDER BY id DESC"
        res = db_query(q, (self.proj, f"%{busca}%", f"%{busca}%"), fetch=True)
        self.ids.rv_historico.data = [{'placa': r[0], 'nome': r[1], 'caps': r[2], 'altura': r[3], 'gps': r[4]} for r in res]

class InventarioApp(App):
    projeto_ativo = StringProperty("")
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TelaMenu(name='menu'))
        sm.add_widget(TelaCadastro(name='cadastro'))
        sm.add_widget(TelaHistorico(name='historico'))
        return sm

if __name__ == '__main__':
    InventarioApp().run()
