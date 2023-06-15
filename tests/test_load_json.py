import json
from datetime import datetime

from dados.modelo import DadosAnalise, DadoFrame

with open('test_json.json', 'r') as file:
    dados = json.load(file)

print(dados)
#print(dados["data_hora_analise"])

analise = DadosAnalise(
    data_hora_analise=datetime.strptime(dados['data_hora_analise'], "%d/%m/%Y %H:%M:%S %f"),
    duracao_analise=dados['duracao_analise'],
    quantidade_de_piscadas=dados['quantidade_de_piscadas'],
    piscadas_por_minuto=dados['piscadas_por_minuto'],
    dados_frames=[],
)

for dado_frame in dados['dados_frames']:
    print(dado_frame)
    analise.dados_frames.append(
        DadoFrame(
            numero_frame=dado_frame['numero_frame'],
            data_hora_frame=dado_frame['data_hora_frame'],
            olho_direito_aberto=dado_frame['olho_direito_aberto'],
            olho_esquerdo_aberto=dado_frame['olho_esquerdo_aberto'],
        )
    )

print(analise)
