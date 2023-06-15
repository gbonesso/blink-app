import logging

from kivy.properties import ObjectProperty
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField
from kivy import platform

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class TelaConfiguracao(MDScreen):
    main_app = ObjectProperty()

    def voltar_button_on_release(self, source_button):
        self.main_app.screen_manager.current = "screen_00"

    def gravar_button_on_release(self, source_button):
        # from kivy.config import Config
        logger.info("debug_eyes_switch.active: {}".format(self.debug_eyes_switch.active))
        self.main_app.config.set('debug', 'debug-eyes', self.debug_eyes_switch.active),
        if platform == "macosx":
            if len(self.min_eye_size_textfield.text) > 0:
                self.main_app.config.set(
                    'cascade-desktop', 'minsize-eyes', int(self.min_eye_size_textfield.text)
                )
                self.main_app.config.set(
                    'cascade-desktop', 'minneighbors-eyes', int(self.min_neighbors_eye_textfield.text)
                )
                self.main_app.config.set(
                    'cascade-desktop', 'minsize-face', int(self.min_face_size_textfield.text)
                )
                self.main_app.config.set(
                    'cascade-desktop', 'minneighbors-face', int(self.min_neighbors_face_textfield.text)
                )
        elif platform == "android":
            if len(self.min_eye_size_textfield.text) > 0:
                self.main_app.config.set(
                    'cascade-mobile', 'minsize-eyes', int(self.min_eye_size_textfield.text)
                )
                self.main_app.config.set(
                    'cascade-mobile', 'minneighbors-eyes', int(self.min_neighbors_eye_textfield.text)
                )
                self.main_app.config.set(
                    'cascade-mobile', 'minsize-face', int(self.min_face_size_textfield.text)
                )
                self.main_app.config.set(
                    'cascade-mobile', 'minneighbors-face', int(self.min_neighbors_face_textfield.text)
                )
        self.main_app.config.write()

    def __init__(self, **kwargs):
        super(TelaConfiguracao, self).__init__(**kwargs)
        layout = MDFloatLayout(
            # orientation='vertical',
            # padding=("10dp", "15dp", "10dp", "15dp"),  # LTRB
            pos_hint={"top": 0.9},
        )
        blink_logo = Image(
            source='assets/Blink_Logo_Branco_Transparente.png',
            size_hint=(1, 0.3),
            pos_hint={"top": 0.95, "center_x": 0.5},
        )
        self.min_eye_size_textfield = MDTextField(
            mode="round",
            fill_color_normal=(1, 1, 1, 1),
            icon_left="numeric",
            # hint_text="aresta mínima de detecção de olhos",
            hint_text="min size - eyes",
            max_text_length=3,
            font_size=24,
            pos_hint={"center_x": 0.25, "center_y": 0.5},
            size_hint=(0.4, None),
            helper_text="minSize - Eyes",
            helper_text_mode="persistent",
            helper_text_color_normal=(1, 1, 1, 1),
            input_filter="int",  # Aceita somente números inteiros
        )
        self.min_neighbors_eye_textfield = MDTextField(
            mode="round",
            fill_color_normal=(1, 1, 1, 1),
            icon_left="numeric",
            hint_text="min neighbors - eyes",
            max_text_length=3,
            font_size=24,
            pos_hint={"center_x": 0.75, "center_y": 0.5},
            size_hint=(0.4, None),
            helper_text="minNeighbors - Eyes",
            helper_text_mode="persistent",
            helper_text_color_normal=(1, 1, 1, 1),
            input_filter="int",  # Aceita somente números inteiros
        )
        self.min_face_size_textfield = MDTextField(
            mode="round",
            fill_color_normal=(1, 1, 1, 1),
            icon_left="numeric",
            # hint_text="aresta mínima de detecção de faces",
            hint_text="min size - faces",
            max_text_length=3,
            font_size=24,
            pos_hint={"center_x": 0.25, "center_y": 0.4},
            size_hint=(0.4, None),
            helper_text="minSize - Faces",
            helper_text_mode="persistent",
            helper_text_color_normal=(1, 1, 1, 1),
            input_filter="int",  # Aceita somente números inteiros
        )
        self.min_neighbors_face_textfield = MDTextField(
            mode="round",
            fill_color_normal=(1, 1, 1, 1),
            icon_left="numeric",
            hint_text="min neighbors - faces",
            max_text_length=3,
            font_size=24,
            pos_hint={"center_x": 0.75, "center_y": 0.4},
            size_hint=(0.4, None),
            helper_text="minNeighbors - Faces",
            helper_text_mode="persistent",
            helper_text_color_normal=(1, 1, 1, 1),
            input_filter="int",  # Aceita somente números inteiros
        )
        self.debug_eyes_switch = MDSwitch(
            pos_hint={"center_x": 0.2, "center_y": 0.3},
            # active=self.main_app.config.getboolean('debug', 'debug-eyes'),
        )
        label_debug_eyes = MDLabel(
            text="Olhos para debug",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_size=28,
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        voltar_button = MDFillRoundFlatButton(
            text="Voltar",
            font_size=28,
            pos_hint={"center_x": 0.3, "center_y": 0.2},
            size_hint=(0.3, None),
            on_release=self.voltar_button_on_release,
            # size_hint_x=0.4,
            # padding=("20dp", "20dp", "20dp", "20dp"),
        )
        gravar_button = MDFillRoundFlatButton(
            text="Gravar",
            font_size=28,
            pos_hint={"center_x": 0.7, "center_y": 0.2},
            size_hint=(0.3, None),
            on_release=self.gravar_button_on_release,
        )
        layout.add_widget(blink_logo)
        layout.add_widget(self.min_eye_size_textfield)
        layout.add_widget(self.min_neighbors_eye_textfield)
        layout.add_widget(self.min_face_size_textfield)
        layout.add_widget(self.min_neighbors_face_textfield)
        layout.add_widget(self.debug_eyes_switch)
        layout.add_widget(label_debug_eyes)
        layout.add_widget(voltar_button)
        layout.add_widget(gravar_button)
        self.add_widget(layout)

    # Método invocado antes da página ser mostrada na tela
    def on_pre_enter(self):
        self.debug_eyes_switch.active = self.main_app.config.getboolean('debug', 'debug-eyes')
        if platform == "macosx" or platform == "windows":
            self.min_eye_size_textfield.text = str(self.main_app.config.getint('cascade-desktop', 'minsize-eyes'))
            self.min_neighbors_eye_textfield.text = str(
                self.main_app.config.getint('cascade-desktop', 'minneighbors-eyes'))
            self.min_face_size_textfield.text = str(self.main_app.config.getint('cascade-desktop', 'minsize-face'))
            self.min_neighbors_face_textfield.text = str(
                self.main_app.config.getint('cascade-desktop', 'minneighbors-face'))
        elif platform == "android":
            self.min_eye_size_textfield.text = str(self.main_app.config.getint('cascade-mobile', 'minsize-eyes'))
            self.min_neighbors_eye_textfield.text = str(
                self.main_app.config.getint('cascade-mobile', 'minneighbors-eyes'))
            self.min_face_size_textfield.text = str(self.main_app.config.getint('cascade-mobile', 'minsize-face'))
            self.min_neighbors_face_textfield.text = str(
                self.main_app.config.getint('cascade-mobile', 'minneighbors-face'))
