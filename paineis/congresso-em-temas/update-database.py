# coding=utf-8
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt
from copy import deepcopy

# Connect to databases
import yaml
import sys
from pathlib import Path 

current_path = Path().resolve()
abs_path = str(current_path.parent)
sys.path.append(abs_path)

server = yaml.load(open(str(current_path.parent.parent / 'dbconfig.yaml'))
con_source = create_engine(server['db_cts'])
con_target = create_engine(server['db_dashes'])

### Getting data from source
propositions = pd.read_sql_query("""
SELECT DISTINCT
  t1.idproposicao,t1.nomeproposicao,t1.tema,t1.tipoproposicao,t1.dataapresentacao,t1.ementa,t1.indexacao,t1.situacao,t1.idecadastro,t1.autor,t1.ufautor,t1.regimetramitacao,t1.ultimodespacho
FROM
  c_camdep.camdep_proposicoes_id t1,
  (SELECT DISTINCT idproposicao, max(capnum) OVER (PARTITION BY idproposicao) capnum FROM c_camdep.camdep_proposicoes_id) t2
WHERE
  t1.idproposicao = t2.idproposicao AND t1.capnum = t2.capnum AND t1.nomeproposicao SIMILAR TO '(PL|PLP|PLV|MPV|PDC|PEC) %%'  AND t1.dataapresentacao >= '2003-01-01'
""", con_source)
print('propositions loaded. Rows: {}'.format(len(propositions)))

proceedings = pd.read_sql_query("""
SELECT DISTINCT
  codproposicao idproposicao, max(datatramitacao) OVER (PARTITION BY codproposicao) data_ultima_tramitacao
FROM
  viz_congresso_tramitacao.proposicoes_tramitadas_periodo
WHERE 
  datatramitacao  >= '2003-01-01'
""", con_source)
print('proceedings loaded. Rows: {}'.format(len(proceedings)))

congressmen = pd.read_sql_query("""
SELECT
  idecadastro,numlegislatura,nomeparlamentar,sexo,legendapartidoeleito,condicao,situacaomandato,ufeleito
FROM
  c_camdep.camdep_deputados_historico
""", con_source)
print('congressmen loaded. Rows: {}'.format(len(congressmen)))

parties = pd.read_sql_query("""
SELECT DISTINCT idpartido, nomepartido FROM c_camdep.camdep_partidos
""", con_source).set_index('idpartido')
print('parties loaded. Rows: {}'.format(len(parties)))

#########################################################################
############################ DATA PROCESSING ############################
#########################################################################


# PROPOSITIONS

## Coleting list of themes
themes = propositions.loc[~propositions.tema.isnull(), 'tema']
themes = themes.apply(lambda x: x.replace(' (utilizado até a legislatura 53)', '')) \
               .drop_duplicates() \
               .apply(lambda x: x.split(';'))
unique_themes = []

for i in themes:
    for theme in i:
        theme = theme.strip(' ')
        if theme not in unique_themes:
            unique_themes.append(theme)

unique_themes.sort()
unique_themes = pd.DataFrame(unique_themes, columns=['Tema'])
unique_themes.index.name = 'cod_tema'
unique_themes.to_csv('themes.csv')

## Cataloging propositions by situation
propositions['descricao_situacao'] = 'Em tramitação'

classification = {
    'Aprovada': [
        'Tranformada',
        'Transformado em Norma Jurídica',
        'Aguardando Apreciação pelo Senado Federal',
        'Aguardando Envio ao Senado Federal',
        'Enviada ao Senado Federal',
        'Aguardando Promulgação',
        'Aguardando Apreciação do Veto',
        'Aguardando Sanção',
        'Aguardando Envio ao Executivo',
        'Vetado Totalmente',
        'Originou'
    ],
    'Arquivada': [
        'Arquivada',
        'Aguardando Despacho de Arquivamento',
        'Aguardando Remessa ao Arquivo',
        'Enviada ao arquivo',
        'Perdeu a eficácia',
        'Transformado em nova proposição'
    ]
}

for situation in tqdm(classification):
    sits = '|'.join(classification[situation])
    propositions.loc[propositions['situacao'].str.contains(sits) == True, 'descricao_situacao'] = situation

## Get and merge proceedings of propositions
propositions = propositions.merge(proceedings, on='idproposicao', how='left')

print("Propositions || OK")


# Congressmen

## Get the congressmen url photo
def get_urlfoto(row):
    return 'http://www.camara.leg.br/internet/deputado/bandep/{}.jpg'.format(row.idecadastro)

congressmen.loc[:, 'urlfoto'] = congressmen.apply(get_urlfoto, axis=1)

print("Congressmen || OK")


# Upload processed data to the target database


## Parlamentares
propositions.to_sql('proposicoes', con_target, schema='dash_temas', if_exists='replace')
print('congressmen updated. Rows = {}'.format(len(propositions)))

congressmen.to_sql('deputados', con_target, schema='dash_temas', if_exists='replace')
print('deputados updated. Rows = {}'.format(len(congressmen)))

## Propositions
parties.to_sql('partidos', con_target, schema='dash_temas', if_exists='replace')
print('partidos updated. Rows = {}'.format(len(parties)))

