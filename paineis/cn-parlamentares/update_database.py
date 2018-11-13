# coding=utf-8
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime
from tqdm import tqdm
from functools import reduce
import unidecode
import re
import operator
import requests

### Connect to databases
from sqlalchemy import create_engine
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
deputados_detalhes = pd.read_sql_query("""
    SELECT DISTINCT
      t1.idecadastro,
      numlegislatura,
      nomeparlamentaratual,
      nomecivil,
      datanascimento,
      partidoatualsigla,
      ufrepresentacaoatual,
      situacaonalegislaturaatual
    FROM
      c_camdep.camdep_deputados_detalhes t1,
      (SELECT DISTINCT
          idecadastro,
          max(capnum) OVER (PARTITION BY idecadastro) capnum
       FROM
          c_camdep.camdep_deputados_detalhes) t2
    WHERE
      t1.idecadastro= t2.idecadastro AND
      t1.capnum = t2.capnum AND
      numlegislatura IN (52,53,54,55);
""", con_source)
print('deputados_datalhes loaded. Rows: {}'.format(len(deputados_detalhes)))

tse_total_votos = pd.read_csv('data/total_votos_2014.csv')
print('tse_total_votos loaded. Rows: {}'.format(len(tse_total_votos)))

tse_candidatos = pd.read_sql("""
    SELECT
      sigla_uf,
      nome_candidato nomecivil,
      numero_candidato numero_votavel,
      data_nascimento datanascimento
    FROM
      c_tse.candidatos_2014
    WHERE
      codigo_cargo = 6 AND
      desc_sit_tot_turno IN ('ELEITO','ELEITO POR MÉDIA','ELEITO POR QP','SUPLENTE')
""", con_source)
print('tse_candidatos loaded. Rows: {}'.format(len(tse_candidatos)))

proposicoes_id = pd.read_sql("""
    SELECT DISTINCT
      t1.idproposicao,
      nomeproposicao,
      tema,
      ementa,
      idecadastro,
      autor,
      ufautor,
      partidoautor,
      dataapresentacao,
      regimetramitacao,
      indexacao,
      linkinteiroteor,
      situacao
    FROM
      c_camdep.camdep_proposicoes_id t1,
      (SELECT DISTINCT
         idproposicao,
         max(capnum) OVER (PARTITION BY idproposicao) capnum
       FROM
         c_camdep.camdep_proposicoes_id) t2
    WHERE
      t1.idproposicao = t2.idproposicao AND
      t1.capnum = t2.capnum AND
      t1.nomeproposicao SIMILAR TO '(PL|PLP|PLV|MPV|PDC|PEC) %%' AND
      EXTRACT(YEAR FROM t1.dataapresentacao) >= 2003
""", con_source)
print('proposicoes_id loaded. Rows: {}'.format(len(proposicoes_id)))

orgaos_membros = pd.read_sql("""
    SELECT
      idecadastro,
      idorgao,
      siglaorgao,
      nomeorgao,
      tipoorgao,
      nomepapel,
      datainicio,
      datafim
    FROM
      br_camdep_v2.orgaos_membros
    WHERE
      datainicio >= '2003-01-01';
""", con_source)

print('orgaos_membros loaded. Rows: {}'.format(len(orgaos_membros)))

votacao_deputado = pd.read_sql("""
    SELECT DISTINCT
      idecadastro,
      codproposicao idproposicao,
      codsessao,
      datavotacao,
      voto,
      partido
    FROM
      c_camdep.camdep_proposicoes_votacao_deputado
    WHERE
      tipo SIMILAR TO '(PL|PLP|PLV|MPV|PDC|PEC)' AND
      datavotacao >= '2003-01-01'
""", con_source)
print('votacao_deputado loaded. Rows: {}'.format(len(votacao_deputado)))

votacao_bancada = pd.read_sql("""
    SELECT DISTINCT
      codproposicao,
      codsessao,
      datavotacao,
      sigla,
      orientacao
    FROM
      c_camdep.camdep_proposicoes_votacao_bancada
    WHERE
      tipo SIMILAR TO '(PL|PLP|PLV|MPV|PDC|PEC)' AND
      datavotacao >= '2003-01-01'
""", con_source)
print('votacao_bancada loaded. Rows: {}'.format(len(votacao_bancada)))

#########################################################################
############################ DATA PROCESSING ############################
#########################################################################


# Parlamentares table


## Count legislatures
legs = deputados_detalhes[['idecadastro', 'numlegislatura']] \
    .groupby('idecadastro').count().to_dict()['numlegislatura']

dep_leg55 = deepcopy(deputados_detalhes.loc[deputados_detalhes.numlegislatura == 55])
dep_leg55['legislaturas'] = dep_leg55.idecadastro.map(legs)

print("Legislatures count || OK")


## Get the URL picture
def get_urlfoto(row):
    return 'http://www.camara.leg.br/internet/deputado/bandep/{}.jpg'.format(row.idecadastro)


dep_leg55.loc[:, 'urlfoto'] = dep_leg55.apply(get_urlfoto, axis=1)

print("Parlamentares URL Photo || OK")


## Get election votes amount
def percent_party(row):
    return row.total_votos / votes_by_parties.total_votos[row.nome_partido]


tse_total_votos = tse_total_votos.dropna()
tse_total_votos.numero_votavel = tse_total_votos.numero_votavel.astype(int)

votes_by_parties = tse_total_votos[['nome_partido', 'total_votos']].groupby('nome_partido').sum()

tse_total_votos.loc[:, 'percent_party'] = tse_total_votos.apply(percent_party, axis=1)

print("Election votes amount || OK")


## Merge the TSE and CAMDEP parlamentares datasets
def tse_unique_id(row):
    return '{}_{}'.format(row.sigla_uf, row.numero_votavel)


def global_unique_id(row):
    name = row.nomecivil.upper().replace(' DE ', '').replace(' ', '')
    name = unidecode.unidecode(name)
    birth = row.datanascimento.year
    return '{}{}'.format(birth, name)


tse_candidatos.numero_votavel = tse_candidatos.numero_votavel.astype(int)
dep_leg55.datanascimento = pd.to_datetime(dep_leg55.datanascimento).dt.date
tse_candidatos.datanascimento = pd.to_datetime(tse_candidatos.datanascimento).dt.date

tse_candidatos.loc[:, 'tse_id'] = tse_candidatos.apply(tse_unique_id, axis=1)
tse_total_votos.loc[:, 'tse_id'] = tse_total_votos.apply(tse_unique_id, axis=1)

tse_candidatos = tse_candidatos.merge(
    tse_total_votos[['total_votos', 'percent_party', 'tse_id']],
    left_on='tse_id', right_on='tse_id', how='left'
)

tse_candidatos.loc[:, 'global_id'] = tse_candidatos.apply(global_unique_id, axis=1)
dep_leg55.loc[:, 'global_id'] = dep_leg55.apply(global_unique_id, axis=1)

### Fixing noise
corrects_id = {
    74558: '1957GIVALDOSAGOUVEIACARIMBAO',
    146949: '1973ROSEANECAVALCANTEFREITAS',
    178851: '1979JOZIANEARAUJONASCIMENTOROCHA',
    178882: '1989ANDRELUISCARVALHORIBEIRO',
    178883: '1977ELIZIANEPEREIRAGAMAFERREIRA',
    178999: '1989BRUNIELEFERREIRADASILVA'
}

for i in corrects_id:
    dep_leg55.loc[dep_leg55.idecadastro == i, 'global_id'] = corrects_id[i]

dep_leg55 = dep_leg55.merge(
    tse_candidatos[['global_id', 'nomecivil', 'total_votos', 'percent_party', 'numero_votavel']],
    left_on='global_id', right_on='global_id', how='left'
)

dep_leg55 = dep_leg55.loc[:, [
    'global_id', 'idecadastro', 'numero_votavel', 'nomeparlamentaratual',
    'nomecivil_y', 'datanascimento', 'ufrepresentacaoatual', 'partidoatualsigla',
    'situacaonalegislaturaatual', 'urlfoto', 'total_votos', 'percent_party', 'legislaturas'
]]

dep_leg55.columns = [
    'global_id', 'idecadastro', 'numero_eleicao', 'nome_social',
    'nome_civil', 'data_nascimento', 'uf_eleicao', 'partido_atual',
    'situacao_exercicio', 'url_foto', 'total_votos', 'percent_party', 'mandatos_desde2003'
]

print("CAMDEP and TSE data merge || OK")

# Propositions data


## Catalog propositions by situation
proposicoes_id.rename(columns={'situacao': 'descricao_situacao'}, inplace=True)
proposicoes_id['situacao'] = 'Em tramitação'

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
    proposicoes_id.loc[proposicoes_id['descricao_situacao'].str.contains(sits) == True, 'situacao'] = situation

print('Catalog propositions by situation || OK')

## Count sponsors (autorias) information
proposicoes_id.idecadastro = np.nan_to_num(proposicoes_id.idecadastro).astype(int)
sponsors = pd.DataFrame(proposicoes_id.idecadastro.value_counts())
sponsors_approved = pd.DataFrame(
    proposicoes_id[proposicoes_id.situacao == 'Aprovada'].idecadastro.value_counts()
)
sponsors.columns = ['apresentacoes']
sponsors_approved.columns = ['apresentacoes_aprovadas']

dep_leg55 = dep_leg55 \
    .merge(sponsors, left_on='idecadastro', right_index=True, how='left') \
    .merge(sponsors_approved, left_on='idecadastro', right_index=True, how='left')

dep_leg55.apresentacoes = np.nan_to_num(dep_leg55.apresentacoes).astype(int)
dep_leg55.apresentacoes_aprovadas = np.nan_to_num(dep_leg55.apresentacoes_aprovadas).astype(int)

dep_leg55.loc[:, 'taxa_sucesso'] = dep_leg55.apresentacoes_aprovadas / dep_leg55.apresentacoes
dep_leg55.loc[:, 'media_apresentacoes'] = np.average(dep_leg55.apresentacoes)
dep_leg55.loc[:, 'media_taxa_sucesso'] = dep_leg55.taxa_sucesso.sum() / len(dep_leg55.taxa_sucesso)

print('Count sponsors information || OK')

# Themes by parlamentares (to table parlamentares_temas)


## Get themes
themes = set()
for i in proposicoes_id.tema:
    if i:
        i = i.replace(' (utilizado até a legislatura 53)', '') \
            .replace('; ', ', ') \
            .split(', ')
        themes = themes.union(i)

### Filter propositions
proposicoes_temas = proposicoes_id[['idecadastro', 'tema']][
    proposicoes_id.idecadastro.isin(dep_leg55.idecadastro)
]

print('Get themes || OK')

## Count themes by parlamentar
parlamentares_tema = pd.DataFrame(columns=['idecadastro'] + list(themes))

dic = {theme: 0 for theme in themes}
for i in dep_leg55.idecadastro.unique():
    dic['idecadastro'] = i
    parlamentares_tema = parlamentares_tema.append(dic, ignore_index=True)
parlamentares_tema = parlamentares_tema.astype(int)

for l in tqdm(proposicoes_temas.to_dict(orient='split')['data']):
    if l[1]:
        l[1] = l[1].replace(' (utilizado até a legislatura 53)', '') \
            .replace('; ', ', ') \
            .split(', ')
        for theme in l[1]:
            parlamentares_tema.loc[parlamentares_tema.idecadastro == l[0], theme] += 1

print("Count themes by parlamentar || OK")


# Committees table


orgaos_membros.idecadastro = np.nan_to_num(orgaos_membros.idecadastro).astype(int)
orgaos_membros = orgaos_membros[
    orgaos_membros.idecadastro.isin(dep_leg55.idecadastro)
]


# Party loyalty


votacao_deputado.idecadastro = np.nan_to_num(votacao_deputado.idecadastro).astype(int)
votacao_deputado = votacao_deputado[
    votacao_deputado.idecadastro.isin(dep_leg55.idecadastro)
]


## Getting parties orientations
def prepare_orientations(sec, dt):
    orientations = votacao_bancada[
        (votacao_bancada.codsessao == sec) &
        (votacao_bancada.datavotacao == dt)
        ][['sigla', 'orientacao']].set_index('sigla').to_dict()['orientacao']

    dic = {}
    for (abbr, orientation) in orientations.items():
        abbr = abbr.replace('Repr.', '').strip('.')
        if not abbr.isupper():
            abbrs = re.findall('[A-Z][^A-Z]*', abbr)
            if 'B' in abbrs:
                abbrs.remove('B')
                if 'Cdo' in abbrs:
                    abbrs.append('PCdoB')
                    abbrs.remove('Cdo')
                    abbrs.remove('P')
                elif 'Tdo' in abbrs:
                    abbrs.append('PTdoB')
                    abbrs.remove('Tdo')
                    abbrs.remove('P')
                elif 'Ptdo' in abbrs:
                    abbrs.append('PTdoB')
                    abbrs.remove('Ptdo')
            for i in abbrs:
                dic[i.upper()] = orientation
        else:
            dic[abbr] = orientation
    return dic


def get_orientation(row):
    try:
        orientation = orientations_dic[row.codsessao][str(row.datavotacao)][row.partido.upper()]
        return orientation
    except KeyError:
        return None


orientations_dic = {}
section_date = votacao_deputado[['codsessao', 'datavotacao']].drop_duplicates()

for sec, dt in tqdm(section_date.to_dict(orient='split')['data']):
    try:
        orientations_dic[sec][str(dt)] = prepare_orientations(sec, dt)
    except KeyError:
        orientations_dic[sec] = {str(dt): prepare_orientations(sec, dt)}

votacao_deputado.loc[:, 'orientacaobancada'] = votacao_deputado.apply(get_orientation, axis=1)

print('Getting parties orientations || OK')

## Calculating the party loyalty
votacao_deputado = votacao_deputado.loc[votacao_deputado.voto != 'Art. 17'] ### Congress president
votacao_deputado.loc[:,'fidelidade'] = 0
votacao_deputado.loc[votacao_deputado.orientacaobancada.isin(['Liberado',None]),'fidelidade'] = 1
votacao_deputado.loc[votacao_deputado.voto == votacao_deputado.orientacaobancada,'fidelidade'] = 1

fidelidade_sum = votacao_deputado[['idecadastro','fidelidade']].groupby('idecadastro').sum()
fidelidade_total = votacao_deputado[['idecadastro','fidelidade']].groupby('idecadastro').count()
fidelidade = fidelidade_sum/fidelidade_total
fidelidade = fidelidade.reset_index()

dep_leg55 = dep_leg55.merge(fidelidade, on='idecadastro', how='left')


# Upload processed data to the target database


## Parlamentares
dep_leg55.to_sql('parlamentares', con_target, schema='dash_parlamentares', if_exists='replace')
print('parlamentares updated. Rows = {}'.format(len(dep_leg55)))

parlamentares_tema.to_sql('parlamentares_temas', con_target, schema='dash_parlamentares', if_exists='replace')
print('parlamentares_temas updated. Rows = {}'.format(len(parlamentares_tema)))

## Propositions
proposicoes_id.to_sql('proposicoes', con_target, schema='dash_parlamentares', if_exists='replace')
print('proposicoes updated. Rows = {}'.format(len(proposicoes_id)))

## Committees
orgaos_membros.to_sql('orgaos', con_target, schema='dash_parlamentares', if_exists='replace')
print('orgaos updated. Rows = {}'.format(len(orgaos_membros)))
