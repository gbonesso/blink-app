from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

kv_card = """
<MD3Card>
    size_hint: 1, 0.2
    #height: "100dp"
    on_press: self.card_on_press(self)

    MDRelativeLayout:

        MDIconButton:
            icon: "dots-vertical"
            pos_hint: {"top": 1, "right": 1}

        MDLabel:
            id: label
            text: root.linha_1
            adaptive_size: True
            color: "grey"
            #pos: "12dp", "12dp"
            pos_hint: {"top": 0.9, "x": 0.05}
            bold: True

        MDLabel:
            id: label
            text: root.linha_2
            adaptive_size: True
            color: "grey"
            #pos: "12dp", "12dp"
            pos_hint: {"top": 0.4, "x": 0.05}
            bold: True
"""


class MD3Card(MDCard):
    linha_1 = StringProperty()
    linha_2 = StringProperty()
    dados_analise = ObjectProperty()
    main_app = ObjectProperty()

    def card_on_press(self, which_card):
        print("Card clicado: {}".format(which_card.dados_analise))
        self.main_app.dados_analise_selecionado = which_card.dados_analise
        self.main_app.screen_manager.current = "screen_04"



class HistoricoAnalises(MDScreen):
    main_app = ObjectProperty()

    def __init__(self, **kwargs):
        super(HistoricoAnalises, self).__init__(**kwargs)
        layout = MDBoxLayout(
            orientation='vertical',
            padding=(5, 5),
            pos_hint={"top": 0.88},
            id="box",
            adaptive_size=True,
            spacing="10dp",  # Espaço vertical entre os Cards
            size_hint=(1, 0.88),
            # height="100dp",
            # md_bg_color=(1, 0, 1, 1),
        )
        Builder.load_string(kv_card)
        for analise in self.main_app.repositorio_dados.get_lista_analises():
            layout.add_widget(
                MD3Card(
                    line_color=(0.2, 0.2, 0.2, 0.8),
                    style="outlined",
                    #linha_1="Data/hora da análise: {}".format(analise.data_hora_analise),
                    linha_1=analise.data_hora_analise.strftime("%d/%m/%Y %H:%M"),
                    linha_2="Piscadas por minuto: {}".format(analise.piscadas_por_minuto),
                    dados_analise=analise,
                    main_app=self.main_app,
                    # width=Window.width * 0.9,
                    #size_hint=(1, 0.2),
                    size_hint_y=None,
                    height="50dp",
                )
            )
        self.add_widget(layout)
