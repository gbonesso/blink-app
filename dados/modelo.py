import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


@dataclass
class DadoFrame:
    numero_frame: int
    data_hora_frame: datetime
    olho_direito_aberto: float  # 0 a 1
    olho_esquerdo_aberto: float  # 0 a 1

    def __hash__(self):
        return hash(repr(self))


@dataclass
class DadosAnalise:
    data_hora_analise: datetime
    duracao_analise: int  # segundos
    quantidade_de_piscadas: int
    piscadas_por_minuto: float
    dados_frames: list

    # Cria um construtor vazio
    # def __init__(self):
    #    pass

    # Cria um objeto JSON com os dados da análise
    def toJSON(self):
        json_list_dados_frames = []
        for dado_frame in self.dados_frames:
            json_list_dados_frames.append(
                {
                    'numero_frame': dado_frame.numero_frame,
                    'data_hora_frame': dado_frame.data_hora_frame.strftime("%d/%m/%Y %H:%M:%S %f"),
                    'olho_direito_aberto': dado_frame.olho_direito_aberto,
                    'olho_esquerdo_aberto': dado_frame.olho_esquerdo_aberto,
                }
            )

        json_obj = {
            'data_hora_analise': self.data_hora_analise.strftime("%d/%m/%Y %H:%M:%S %f"),
            'duracao_analise': self.duracao_analise,
            'quantidade_de_piscadas': self.quantidade_de_piscadas,
            'piscadas_por_minuto': self.piscadas_por_minuto,
            'dados_frames': json_list_dados_frames,
        }

        return json_obj

    # Popula os dados da análise com dados JSON
    def fromJSON(self, json_obj):
        self.data_hora_analise = datetime.strptime(json_obj['data_hora_analise'], "%d/%m/%Y %H:%M:%S %f")
        self.duracao_analise = json_obj['duracao_analise']
        self.quantidade_de_piscadas = json_obj['quantidade_de_piscadas']
        self.piscadas_por_minuto = json_obj['piscadas_por_minuto']
        self.dados_frames = []

        for dado_frame in json_obj['dados_frames']:
            logger.info("fromJSON - dado_frame: {}".format(dado_frame))
            self.dados_frames.append(
                DadoFrame(
                    numero_frame=dado_frame['numero_frame'],
                    data_hora_frame=dado_frame['data_hora_frame'],
                    olho_direito_aberto=dado_frame['olho_direito_aberto'],
                    olho_esquerdo_aberto=dado_frame['olho_esquerdo_aberto'],
                )
            )

    def get_duracao(self):
        dt_frame_inicial = datetime.strptime(self.dados_frames[0].data_hora_frame, "%d/%m/%Y %H:%M:%S %f")
        qt_frames = len(self.dados_frames)
        dt_frame_final = datetime.strptime(self.dados_frames[qt_frames - 1].data_hora_frame, "%d/%m/%Y %H:%M:%S %f")
        duracao_segundos = (dt_frame_final - dt_frame_inicial).seconds + (dt_frame_final - dt_frame_inicial).microseconds / 1000000
        logger.info("dt_frame_inicial: {} dt_frame_final: {} duração seg: {}".format(
            dt_frame_inicial, dt_frame_final, duracao_segundos))

