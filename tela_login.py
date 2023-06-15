import logging

from kivy.properties import ObjectProperty
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField

from cadastro_utils import login

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class TelaLogin(MDScreen):
    main_app = ObjectProperty()

    def voltar_button_on_release(self, source_button):
        self.main_app.screen_manager.current = "screen_00"

    def login_button_on_release(self, source_button):
        retorno_login = login(
            self.user_textfield.text,
            self.password_textfield.text,
        )
        if retorno_login == "Login efetuado com sucesso!":
            self.main_app.habilita_menu()
        logger.info("retorno_login: {}".format(retorno_login))
        self.main_app.snackbar_show(retorno_login)

    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        # ToDo: Fazer o ajuste com base no tamanho real do AppBar
        layout = MDFloatLayout(
            pos_hint={"top": 0.9},
        )
        blink_logo = Image(
            source='assets/Blink_Logo_Branco_Transparente.png',
            size_hint=(1, 0.3),
            pos_hint={"top": 0.95, "center_x": 0.5},
        )
        self.user_textfield = MDTextField(
            mode="round",
            fill_color_normal=(1, 1, 1, 1),
            icon_left="account",
            hint_text="Usuário",
            max_text_length=10,
            font_size=24,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.7, None),
        )
        self.password_textfield = MDTextField(
            mode="round",
            fill_color_normal=(1, 1, 1, 1),
            icon_left="key-variant",
            hint_text="Senha",
            max_text_length=10,
            password=True,
            font_size=24,
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            size_hint=(0.7, None),
        )
        voltar_button = MDFillRoundFlatButton(
            text="Voltar",
            font_size=28,
            pos_hint={"center_x": 0.3, "center_y": 0.3},
            size_hint=(0.3, None),
            on_release=self.voltar_button_on_release,
        )
        login_button = MDFillRoundFlatButton(
            text="Login",
            font_size=28,
            pos_hint={"center_x": 0.7, "center_y": 0.3},
            size_hint=(0.3, None),
            on_release=self.login_button_on_release,
        )
        self.label_info = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=(1, 0, 0, 1),
            font_size=28,
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.25},
        )

        layout.add_widget(blink_logo)
        layout.add_widget(self.user_textfield)
        layout.add_widget(self.password_textfield)
        layout.add_widget(voltar_button)
        layout.add_widget(login_button)
        layout.add_widget(self.label_info)
        self.add_widget(layout)
