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
            markup: True
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            padding: 10, 10
            text:
                "O Blink é um aplicativo para dispositivos móveis que monitora a condição de pacientes que sofrem" +\
                "de blefaroespasmo através da avaliação da frequência das piscadas do paciente. \\n\\n" +\
                "Ele foi desenvolvido para a disciplina Desenvolvimento de Aplicativos para Inovação Tecnológica " +\
                "do programa de Mestrado Profissional em Inovação Tecnológica do Instituto de Ciência e Tecnologia " +\
                "da Universidade Federal de São Paulo - Campus São José dos Campos. \\n\\n" +\
                "A responsável pela disciplina é a [b]Regina Celia Coelho[/b] e a mentoria foi feita pelo " +\
                "[b]Guilherme Melo Dos Santos[/b]. \\n\\n" +\
                "O código é público e está disponível em [i]https://github.com/gbonesso/blink-app[/i].\\n\\n" +\
                "O autor pode ser contatado pelo email [i]gustavo_bonesso@hotmail.com[/i]."

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
