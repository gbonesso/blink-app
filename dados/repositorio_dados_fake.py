from datetime import datetime

from dados.modelo import DadoFrame, DadosAnalise


class RepositorioDadosAnalise:
    #lista_analises: []

    def __init__(self):
        self.lista_analises = [];
        self.lista_analises.append(DadosAnalise(
            data_hora_analise=datetime(2023, 5, 29, 18, 10),
            duracao_analise=125,
            quantidade_de_piscadas=85,
            piscadas_por_minuto=41,
            dados_frames={
                DadoFrame(numero_frame=1, data_hora_frame=datetime(2023, 5, 29, 18, 10, 1, 25), olho_direito_aberto=0., olho_esquerdo_aberto=0.),
                DadoFrame(numero_frame=2, data_hora_frame=datetime(2023, 5, 29, 18, 10, 1, 50), olho_direito_aberto=0.1, olho_esquerdo_aberto=0.1),
                DadoFrame(numero_frame=3, data_hora_frame=datetime(2023, 5, 29, 18, 10, 1, 70), olho_direito_aberto=0.0, olho_esquerdo_aberto=0.4),
            }
        ))
        self.lista_analises.append(DadosAnalise(
            data_hora_analise=datetime(2023, 5, 28, 10, 5),
            duracao_analise=120,
            quantidade_de_piscadas=20,
            piscadas_por_minuto=10,
            dados_frames={
                DadoFrame(numero_frame=1, data_hora_frame=datetime(2023, 5, 28, 10, 5, 1, 25), olho_direito_aberto=0., olho_esquerdo_aberto=0.),
                DadoFrame(numero_frame=2, data_hora_frame=datetime(2023, 5, 28, 10, 5, 1, 50), olho_direito_aberto=0.5, olho_esquerdo_aberto=0.6),
                DadoFrame(numero_frame=3, data_hora_frame=datetime(2023, 5, 28, 10, 5, 1, 70), olho_direito_aberto=0.2, olho_esquerdo_aberto=0.9),
            }
        ))

    def get_lista_analises(self):
        return self.lista_analises

