from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatButton

kv_blink_app_name_label = """ 
Label:
    text:"Blink"
    color:1,1,1,1
    font_name:"fonts/Oswald-Medium.ttf"
    halign:"center"
    size_hint_y: 0.2
    size_hint_x: 1.0
    font_size: self.width/5
"""


class TelaInicial(MDScreen):
    main_app = ObjectProperty()

    def vai_para_pagina_login(self, source_button):
        self.main_app.screen_manager.current = "screen_05"

    def vai_para_pagina_cadastro(self, source_button):
        self.main_app.screen_manager.current = "screen_06"

    def __init__(self, **kwargs):
        super(TelaInicial, self).__init__(**kwargs)
        layout = BoxLayout(
            orientation='vertical',
            padding=("10dp", "15dp", "10dp", "15dp"),  # LTRB
            pos_hint={"top": 0.9},
        )
        blink_logo = Image(
            source='assets/Blink_Logo_Branco_Transparente.png',
            size_hint_y=0.3,
        )
        unifesp_logo = Image(
            source='assets/Unifesp_simples_verde_negativo_RGB.png',
            size_hint_y=0.3,
        )
        login_button = MDFillRoundFlatButton(
            text="Login",
            font_size=28,
            pos_hint={"center_x": 0.5},
            size_hint_x=None,
            width="200dp",
            on_release=self.vai_para_pagina_login,
            # O padding para botoes é entre o texto do botão e a borda...
            #padding=("20dp", "20dp", "20dp", "20dp"),
        )
        cadastrar_button = MDFillRoundFlatButton(
            text="Cadastrar",
            font_size=28,
            pos_hint={"center_x": 0.5},
            size_hint_x=None,
            width="200dp",
            on_release=self.vai_para_pagina_cadastro,
            #padding=("20dp", "20dp", "20dp", "20dp"),
        )
        blink_app_name_label = Builder.load_string(kv_blink_app_name_label)
        layout.add_widget(blink_logo)
        layout.add_widget(blink_app_name_label)
        layout.add_widget(login_button)
        layout.add_widget(
            MDFillRoundFlatButton(
                text="Espacador...",
                font_size=28,
                pos_hint={"center_x": 0.5},
                opacity=0,
            )
        )
        layout.add_widget(cadastrar_button)
        layout.add_widget(unifesp_logo)
        self.add_widget(layout)
