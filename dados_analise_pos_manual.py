import logging

from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
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

    def __init__(self, **kwargs):
        super(TelaDadosAnalise, self).__init__(**kwargs)

        # Linha "Data da Análise"
        self.add_widget(
            MDLabel(
                text="Data da análise",
                pos_hint={"x": 0.1, "center_y": 0.8},
            )
        )
        self.label_data_analise = MDLabel(
            text="DD/MM/YYYY HH:MI",
            pos_hint={"x": 0.6, "center_y": 0.8},
        )
        self.add_widget(self.label_data_analise)
        # Linha "Duração"
        self.add_widget(
            MDLabel(
                text="Duração",
                pos_hint={"x": 0.1, "center_y": 0.75},
            )
        )
        self.label_duracao = MDLabel(
            text="MI:SS",
            pos_hint={"x": 0.6, "center_y": 0.75},
        )
        self.add_widget(self.label_duracao)
        # Linha "Qt de Piscadas"
        self.add_widget(
            MDLabel(
                text="Quantidade de Piscadas",
                pos_hint={"x": 0.1, "center_y": 0.7},
            )
        )
        self.label_qt_piscadas = MDLabel(
            text="NN",
            pos_hint={"x": 0.6, "center_y": 0.7},
        )
        self.add_widget(self.label_qt_piscadas)
        # Linha "Frequência"
        self.add_widget(
            MDLabel(
                text="Frequência das Piscadas",
                pos_hint={"x": 0.1, "center_y": 0.65},
            )
        )
        self.label_frequencia = MDLabel(
            text="NN/min",
            pos_hint={"x": 0.6, "center_y": 0.65},
        )
        self.add_widget(self.label_frequencia)
        # Linha FPS
        self.add_widget(
            MDLabel(
                text="FPS",
                pos_hint={"x": 0.1, "center_y": 0.60},
            )
        )
        self.label_fps = MDLabel(
            text="fps",
            pos_hint={"x": 0.6, "center_y": 0.60},
        )
        self.add_widget(self.label_fps)
        # Labels dos gráficos
        self.add_widget(
            MDLabel(
                text="D",
                pos_hint={"x": 0.05, "center_y": 0.45},
                size_hint=(None, 0.2),
                font_style="H2",
            )
        )
        self.add_widget(
            MDLabel(
                text="E",
                pos_hint={"x": 0.05, "center_y": 0.15},
                size_hint=(None, 0.2),
                font_style="H2",
            )
        )

    # Atualiza a tela com os dados da análise selecionada no histórico...
    def on_pre_enter(self):
        # logger.info("on_enter...")
        self.label_data_analise.text = "{}".format(
            self.main_app.dados_analise_selecionado.data_hora_analise.strftime("%d/%m/%Y %H:%M")
        )
        duracao = self.main_app.dados_analise_selecionado.get_duracao()
        qt_piscadas_olho_direito, qt_piscadas_olho_esquerdo = self.main_app.dados_analise_selecionado.get_qt_piscadas()
        frequencia_piscadas_olho_direito = qt_piscadas_olho_direito / duracao * 60  # Piscadas / min
        frequencia_piscadas_olho_esquerdo = qt_piscadas_olho_esquerdo / duracao * 60  # Piscadas / min
        self.label_duracao.text = "{:.2f}seg".format(duracao)
        self.label_qt_piscadas.text = "D: {} - E: {}".format(qt_piscadas_olho_direito, qt_piscadas_olho_esquerdo)
        self.label_frequencia.text = "D: {:.2f}/min - E: {:.2f}/min".format(frequencia_piscadas_olho_direito,
                                                                            frequencia_piscadas_olho_esquerdo)
        fps = len(self.main_app.dados_analise_selecionado.dados_frames) / duracao
        self.label_fps.text = "{:.2f}fps".format(fps)

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
            self.remove_widget(self.right_eye_graph_widget)
            self.remove_widget(self.left_eye_graph_widget)

        # Monta o gráfico - Olho direito
        self.right_eye_graph_widget = Graph(
            xlabel='X', ylabel='Y', x_ticks_minor=5,
            x_ticks_major=25, y_ticks_major=1,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, xmin=-0,
            xmax=len(lista_pontos_olho_direito),
            ymin=0, ymax=1,
            pos_hint={"x": 0.1, "center_y": 0.4},
            size_hint=(0.9, 0.3),
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
            pos_hint={"x": 0.1, "center_y": 0.1},
            size_hint=(0.9, 0.3),

        )
        plot = LinePlot(color=[0, 0, 1, 1], line_width=4)
        plot.points = lista_pontos_olho_esquerdo
        self.left_eye_graph_widget.add_plot(plot)

        self.add_widget(self.right_eye_graph_widget)
        self.add_widget(self.left_eye_graph_widget)

        logger.info("duracao análise: {}".format(self.main_app.dados_analise_selecionado.get_duracao()))
