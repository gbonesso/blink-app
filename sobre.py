from kivy.lang import Builder
from kivymd.uix.screen import MDScreen


kv_scroll_view = """ 
ScrollView:
    do_scroll_x: False
    do_scroll_y: True
    pos_hint: {"top": 0.85}

    GridLayout:
        id: grid
        cols: 1
        spacing: 10
        size_hint_y: None
        height: self.minimum_height * 1.1  # required to size GridLayout

        Image:
            source: 'assets/Blink_Logo_Branco_Transparente.png'
            size_hint_y: None
            #size_hint_x: None
            #width: grid.width / 2
            #height: self.texture_size[1]
            padding: 10, 10
            center_x: self.center_x

        Label:
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            padding: 10, 10
            text:
                'Texto teste texto teste sobre...\\n' * 20

        Image:
            source: 'assets/Unifesp_simples_verde_negativo_RGB.png'
            size_hint_y: None
            padding: 10, 10
            center_x: self.center_x
"""

# ToDo: Finalizar Tela Sobre
class Sobre(MDScreen):
    def __init__(self, **kwargs):
        super(Sobre, self).__init__(**kwargs)
        self.add_widget(Builder.load_string(kv_scroll_view))
