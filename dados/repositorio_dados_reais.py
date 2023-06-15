from datetime import datetime
import os
import logging
import json

from dados.modelo import DadoFrame, DadosAnalise
from cadastro_utils import get_storage_path

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class RepositorioDadosAnalise:

    def __init__(self):
        self.lista_analises = []
        file_folder = os.path.join(get_storage_path(), "json_data")
        if not os.path.isdir(file_folder):
            os.mkdir(file_folder)
        for file in os.listdir(os.path.join(get_storage_path(), "json_data")):
            if file.endswith(".json"):
                file_path = os.path.join(get_storage_path(), "json_data", file)
                logger.info(file_path)

                with open(file_path, 'r') as analysis_file:
                    dados = json.load(analysis_file)

                logger.info(dados)
                # logger.info(dados["data_hora_analise"])

                analise = DadosAnalise(
                    data_hora_analise=datetime.strptime(dados['data_hora_analise'], "%d/%m/%Y %H:%M:%S %f"),
                    duracao_analise=dados['duracao_analise'],
                    quantidade_de_piscadas=dados['quantidade_de_piscadas'],
                    piscadas_por_minuto=dados['piscadas_por_minuto'],
                    dados_frames=[],
                )

                for dado_frame in dados['dados_frames']:
                    logger.info(dado_frame)
                    analise.dados_frames.append(
                        DadoFrame(
                            numero_frame=dado_frame['numero_frame'],
                            data_hora_frame=dado_frame['data_hora_frame'],
                            olho_direito_aberto=dado_frame['olho_direito_aberto'],
                            olho_esquerdo_aberto=dado_frame['olho_esquerdo_aberto'],
                        )
                    )

                self.lista_analises.append(analise)

    def get_lista_analises(self):
        return self.lista_analises
