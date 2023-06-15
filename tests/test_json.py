import json

from dados.repositorio_dados_fake import RepositorioDadosAnalise

dados = RepositorioDadosAnalise()
#print(dados.lista_analises)

analise = dados.lista_analises[0]
json_list_dados_frames = []
for dado_frame in analise.dados_frames:
    json_list_dados_frames.append(
        {
            'numero_frame': dado_frame.numero_frame,
            'data_hora_frame': dado_frame.data_hora_frame.strftime("%d/%m/%Y %H:%M:%S %f"),
            'olho_direito_aberto': dado_frame.olho_direito_aberto,
            'olho_esquerdo_aberto': dado_frame.olho_esquerdo_aberto,
        }
    )

#print(json.dumps(json_list_dados_frames))

json_obj = {
    'data_hora_analise': analise.data_hora_analise.strftime("%d/%m/%Y %H:%M:%S %f"),
    'duracao_analise': analise.duracao_analise,
    'quantidade_de_piscadas': analise.quantidade_de_piscadas,
    'piscadas_por_minuto': analise.piscadas_por_minuto,
    'dados_frames': json_list_dados_frames,
}

print(json_obj)

with open("test_json.json", "w", encoding="utf-8") as file:
    json.dump(json_obj, file, ensure_ascii=False, indent=4)
#print()

#print(json.dumps(analise, indent=4, sort_keys=True, default=str))


