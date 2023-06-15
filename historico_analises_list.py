import logging

from kivy.properties import ObjectProperty
from kivymd.uix.list import TwoLineListItem, MDList
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class MinhaTwoLineListItem(TwoLineListItem):
    dados_analise = ObjectProperty()
    main_app = ObjectProperty()

    def __init__(self, **kwargs):
        super(MinhaTwoLineListItem, self).__init__(**kwargs)
        self.bind(on_press=self.press)

    def press(self, item_source):
        logger.info("MinhaTwoLineListItem.on_press: {}".format(item_source))
        self.main_app.dados_analise_selecionado = item_source.dados_analise
        self.main_app.screen_manager.current = "screen_04"


class HistoricoAnalises(MDScreen):
    main_app = ObjectProperty()
    scroll_view = ObjectProperty()
    container_list = ObjectProperty()

    def __init__(self, **kwargs):
        super(HistoricoAnalises, self).__init__(**kwargs)
        self.scroll_view = MDScrollView(
            pos_hint={"top": 0.85},
            size_hint=(1, 0.85),
            do_scroll_y=True,
            do_scroll_x=False,
        )
        self.add_widget(self.scroll_view)

    def on_pre_enter(self):
        if self.container_list is not None:
            self.scroll_view.remove_widget(self.container_list)
        self.container_list = MDList()
        self.scroll_view.add_widget(self.container_list)

        for analise in self.main_app.repositorio_dados.get_lista_analises():
            self.container_list.add_widget(
                MinhaTwoLineListItem(
                    text=analise.data_hora_analise.strftime("%d/%m/%Y %H:%M"),
                    secondary_text="Piscadas por minuto: {}".format(analise.piscadas_por_minuto),
                    dados_analise=analise,
                    main_app=self.main_app,
                )
            )
