import logging

from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

# ***Kivy Garden - Graph
from kivy_garden.graph import Graph, LinePlot

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class TelaDadosAnalise(MDScreen):
    main_app = ObjectProperty()
    right_eye_graph_widget = ObjectProperty()
    left_eye_graph_widget = ObjectProperty()
    layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(TelaDadosAnalise, self).__init__(**kwargs)
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=(5, 5),
            pos_hint={"top": 0.88},
            id="box",
            adaptive_size=True,
            spacing="10dp",  # Espaço vertical entre os Cards
            size_hint=(1, 0.50),
            # height="100dp",
            # md_bg_color=(1, 0, 1, 1),
        )
        # Monta o Grid
        grid_layout = MDGridLayout(cols=2, row_force_default=True, row_default_height="50dp")
        # Linha "Data da Análise"
        grid_layout.add_widget(MDLabel(text="Data da análise"))
        self.label_data_analise = MDLabel(text="DD/MM/YYYY HH:MI")
        grid_layout.add_widget(self.label_data_analise)
        # Linha "Duração"
        grid_layout.add_widget(MDLabel(text="Duração"))
        self.label_duracao = MDLabel(text="MI:SS")
        grid_layout.add_widget(self.label_duracao)
        # Linha "Qt de Piscadas"
        grid_layout.add_widget(MDLabel(text="Quantidade de Piscadas"))
        self.label_qt_piscadas = MDLabel(text="NN")
        grid_layout.add_widget(self.label_qt_piscadas)
        # Linha "Frequência"
        grid_layout.add_widget(MDLabel(text="Frequência"))
        self.label_frequencia = MDLabel(text="NN/min")
        grid_layout.add_widget(self.label_frequencia)

        self.layout.add_widget(grid_layout)

        self.add_widget(self.layout)

    # Atualiza a tela com os dados da análise selecionada no histórico...
    def on_pre_enter(self):
        # logger.info("on_enter...")
        self.label_data_analise.text = "{}".format(
            self.main_app.dados_analise_selecionado.data_hora_analise.strftime("%d/%m/%Y %H:%M")
        )
        self.label_duracao.text = "{}".format(
            self.main_app.dados_analise_selecionado.duracao_analise
        )
        self.label_qt_piscadas.text = "{}".format(
            self.main_app.dados_analise_selecionado.quantidade_de_piscadas
        )
        self.label_frequencia.text = "{}".format(
            self.main_app.dados_analise_selecionado.piscadas_por_minuto
        )

        # Monta a lista de pontos a partir dos dados da análise
        lista_pontos_olho_direito = []
        lista_pontos_olho_esquerdo = []
        x = 0
        for dado_frame in self.main_app.dados_analise_selecionado.dados_frames:
            lista_pontos_olho_direito.append((x, dado_frame.olho_direito_aberto))
            lista_pontos_olho_esquerdo.append((x, dado_frame.olho_esquerdo_aberto))
            x += 1

        logger.info("lista_pontos olho direito: {}".format(lista_pontos_olho_direito))
        logger.info("lista_pontos olho esquerdo: {}".format(lista_pontos_olho_esquerdo))

        # Primeiro remove o gráfico atual, se ele estiver lá...
        if self.right_eye_graph_widget is not None:
            self.layout.remove_widget(self.right_eye_graph_widget)
            self.layout.remove_widget(self.left_eye_graph_widget)

        # Monta o gráfico - Olho direito
        self.right_eye_graph_widget = Graph(
            xlabel='X', ylabel='Y', x_ticks_minor=5,
            x_ticks_major=25, y_ticks_major=1,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, xmin=-0,
            xmax=len(lista_pontos_olho_direito),
            ymin=0, ymax=1,
        )
        plot = LinePlot(color=[0, 1, 0, 1], line_width=4)
        plot.points = lista_pontos_olho_direito
        self.right_eye_graph_widget.add_plot(plot)

        # Monta o gráfico - olho esquerdo
        self.left_eye_graph_widget = Graph(
            xlabel='X', ylabel='Y', x_ticks_minor=5,
            x_ticks_major=25, y_ticks_major=1,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, xmin=-0,
            xmax=len(lista_pontos_olho_esquerdo),
            ymin=0, ymax=1,
        )
        plot = LinePlot(color=[0, 0, 1, 1], line_width=4)
        plot.points = lista_pontos_olho_esquerdo
        self.left_eye_graph_widget.add_plot(plot)

        self.layout.add_widget(self.right_eye_graph_widget)
        self.layout.add_widget(self.left_eye_graph_widget)
