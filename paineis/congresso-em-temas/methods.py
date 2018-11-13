# coding=utf-8
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import operator
import pandas as pd
import plotly.graph_objs as go
import requests
import urllib
import styles
import utils


def propositions_filter(themes_list, years_range):
    data = requests.get('http://35.192.83.177:5006/proposicoes?tema={}&periodo={}'.format(themes_list, years_range)).json()['data']
    return data

def congressman_table(themes_list, years_range):
    data = requests.get('http://35.192.83.177:5006/parlamentares?tema={}&periodo={}'.format(themes_list, years_range)).json()['data']
    return data

def political_partie_filter(themes_list, years_range):
    data = requests.get('http://35.192.83.177:5006/partidos?tema={}&periodo={}'.format(themes_list, years_range)).json()['data']
    return data

def propositions_status_amount(df_json, status=None):
    df = pd.read_json(df_json, orient='split')

    if status != None:
	df = df[df.descricao_situacao == status]
    return len(df)

def propositions_type_amount(df_json, proposition_type):
    df = pd.read_json(df_json, orient='split')
    df = df[df.nomeproposicao.str.startswith(proposition_type)]
    return len(df)

def propositions_type_disaggregated(df_json, proposition_type):
    df = pd.read_json(df_json, orient='split')
    df = df[df.nomeproposicao.str.startswith(proposition_type)]

    approved = len(df[df.descricao_situacao == 'Aprovada'])
    processing = len(df[df.descricao_situacao == 'Em tramitação'])
    archived = len(df[df.descricao_situacao == 'Arquivada'])

    style = {'font-weight': 'bold', 'float': 'left', 'width': 50, 'text-align': 'right'}

    approved = html.Div(approved, style=style)
    processing = html.Div(processing, style=style)
    archived = html.Div(archived, style=style)

    div = html.Div(
        children=[
            html.Br(),
            html.Div([approved, " Aprovadas"]),
            html.Div([processing, " Em tramitação"]),
            html.Div([archived, " Arquivadas"])
        ]
    )

    return div

def approved_presented_graph(df_json, years_range):
    df = pd.read_json(df_json, orient='split')
    df['dataapresentacao'] = df['dataapresentacao'].map(
        lambda x: pd.to_datetime(x, format='%Y-%m-%dT%H:%M:%S.000Z')
    )
    df['data_ultima_tramitacao'] = df['data_ultima_tramitacao'].map(
        lambda x: pd.to_datetime(x, format='%Y-%m-%dT%H:%M:%S.000Z')
    )

    approved = df[df['descricao_situacao'] == 'Aprovada']
    approved = approved[
        (approved['data_ultima_tramitacao'] <= '{}-01-01'.format(years_range[1] + 1)) &
        (approved['data_ultima_tramitacao'] >= '{}-01-01'.format(years_range[0]))
        ]

    approved['dataapresentacao'] = approved['dataapresentacao'].map(
        lambda x: pd.to_datetime(100 * x.year + x.month, format='%Y%m')
    )

    approved_series = approved[['idproposicao', 'data_ultima_tramitacao']].groupby('da$
    approved_series = approved_series.resample('Y').sum()
    approved_series.index = approved_series.index.map(lambda x: x.year)

    presented = df[
        (df['dataapresentacao'] <= '{}-01-01'.format(years_range[1] + 1)) &
        (df['dataapresentacao'] >= '{}-01-01'.format(years_range[0]))
        ]
    presented['dataapresentacao'] = presented['dataapresentacao'].map(
        lambda x: pd.to_datetime(100 * x.year + x.month, format='%Y%m')
    )

    presented_series = presented[['idproposicao', 'dataapresentacao']].groupby('dataap$
    presented_series = presented_series.resample('Y').sum()
    presented_series.index = presented_series.index.map(lambda x: x.year)

    data1 = go.Bar(
        x=presented_series.index,
        y=presented_series['idproposicao'],
        name='Apresentadas',
        marker={'color': "#00B3E0"}
    )
    data2 = go.Bar(
        x=approved_series.index,
        y=approved_series['idproposicao'],
        name='Aprovadas',
        marker={'color': "#007592"}
    )

    layout = go.Layout(
        legend=dict(orientation="h", x=0.4),
    )

    fig = go.Figure(data=[data1, data2], layout=layout)

    return dcc.Graph(id='approved_presented_graph', figure=fig)

def propositions_table_pretty(propositions_json, congressmen_json):
    propositions = pd.read_json(propositions_json, orient='split') \
        .sort_values('data_ultima_tramitacao', ascending=0).drop_duplicates()

    congressmen = pd.read_json(congressmen_json, orient='split')[[
        'idecadastro', 'legendapartidoeleito', 'ufeleito'
    ]]

    propositions.dataapresentacao = propositions.dataapresentacao.apply(
        lambda x: '{2}/{1}/{0}'.format(*x[:10].split('-')))
    propositions.data_ultima_tramitacao = propositions.data_ultima_tramitacao.apply(
        lambda x: '{2}/{1}/{0}'.format(*x[:10].split('-')))

    df = propositions.merge(congressmen,
                            left_on='idecadastro',
                            right_on='idecadastro',
                            how='left')
    df = df[[
        'tema', 'nomeproposicao', 'autor', 'legendapartidoeleito', 'ufeleito',
        'dataapresentacao', 'data_ultima_tramitacao', 'situacao', 'descricao_situacao'
    ]]

    df.columns = [
        'Tema(s)', 'Proposição', 'Autor', 'Partido Eleito', 'UF',
        'Apresentação', 'Última tramitação', 'Descrição da Situação', 'Situação',
    ]

    df_json = df.to_json(date_format='iso', orient='split')
    return df_json

def congressmen_ranking(congressmen_json):
    df = pd.read_json(congressmen_json, orient='split').sort_values('autorias', ascending=False)
    df = df.drop_duplicates('idecadastro')

    ranking = []
    for index in df[:4].index:
        style = {
            'font-family': 'Lato, sans-serif',
            'font-weight': 'bold',
            'color': '#515151',
            'font-size': '14px',
            'border': 'none',
        }

        info = [

            html.Div(
                html.A(
                    df['nomeparlamentar'][index],
                    href='http://www.camara.leg.br/Internet/Deputado/dep_Detalhe.asp?id={}'.format(df['idecadastro'][index]),
                    target='_blank',
                    style={'text-decoration': 'none', 'color': 'inherit'}
                ),
                style={
                    'font-size': '18px',
                    'color': '#007592'
                }),
	    html.Div('{} - {}'.format(df['legendapartidoeleito'][index], df['ufeleito'][index])),
            html.Div('{0:.0f} Proposições'.format(df['autorias'][index]), style={'margin-bottom': 17})

        ]

        table = html.Table(
            html.Tr([
                html.Td(utils.html_img(
                    df['urlfoto'][index],
                    local=False,
                    style={'width': 70}
                ),
                    style={'border': 'none', 'padding': 0}),
                html.Td(info, style=style)
            ])
        )

        ranking.append(table)

    return ranking

def political_parties_ranking(df_json):
    df = pd.read_json(df_json, orient='split').sort_values('autorias', ascending=False)

    style = {
        'font-size': '14px',
        'border': 'none',
        'font-family': 'Lato, sans-serif',
        'font-weight': 'bold',
        'color': '#515151'
    }

    ranking = []
    for index in df[:5].index:
        info = [

            html.Div('{0:.0f} Proposições'.format(df['autorias'][index])),
            html.Div('{0:.0f} Autores'.format(df['autores'][index]))

        ]

        table = html.Table(
            html.Tr([
                html.Td(
                    html.Div(
                        df['idpartido'][index],
                        style={
                            'width': 120,
                            'font-size': 35,
                            'text-align': 'center',
                            'color': '#007592'
                        }
                    ),
                    style=style
		),
                html.Td(info, style=style)
            ])
        )

        ranking.append(table)

    return ranking

def states_ranking(df_json):
    congressmen = pd.read_json(df_json, orient='split')
    sponsors = congressmen[['ufeleito', 'autorias']].groupby('ufeleito').sum()

    df = gp.read_file("support-files/br-states.json")
    df = df.merge(sponsors, left_on='id', right_index=True, how='left')

    max_sponsors = df.autorias.max()
    bounds = [int(i) for i in np.linspace(0, max_sponsors, 6)]
    levels = []
    for i in range(len(bounds) - 2):
        levels.append("{} - {}".format(bounds[i], bounds[i + 1]))
    levels.append("> {}".format(bounds[-2]))

    colors = ['#00B3E0', '#00A3CC', '#0093B8', '#007592', '#006078']
    color_match = dict()
    for i in range(len(bounds) - 1):
        for k in range(bounds[i], bounds[i + 1] + 1):
            color_match[k] = colors[i]

    layout = dict(
        hovermode='closest',
        legend=dict(x=0.1, y=0.2),
        xaxis=dict(
            range=[-75, -34],
            showgrid=False,
            zeroline=False,
            showticklabels=False
	),
        yaxis=dict(
            range=[-37, 8],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        margin={i: 20 for i in ['t', 'b', 'r', 'l']},
        width=480,
        height=500
    )
    plot_data = []
    for index, row in df.iterrows():
        if df['geometry'][index].type == 'Polygon':
            x, y = row.geometry.exterior.xy
            c_x, c_y = row.geometry.centroid.xy
        else:
            print('stop')
        county_outline = dict(
            type='scatter',
            mode='lines',
            showlegend=False,
            line=dict(color='black', width=0.5),
            x=x, y=y,
            fill='toself',
            fillcolor=color_match[row['autorias']],
            hoverinfo='none'
        )
        hover_point = dict(
            type='scatter',
            showlegend=False,
            legendgroup="centroids",
            name=row.nome,
            text='Proposições: ' + str(row['autorias']),
            marker=dict(opacity=0),
            x=c_x, y=c_y,
            hoverinfo='name+text'
        )
        plot_data.append(county_outline)
        plot_data.append(hover_point)

    for lev in levels:
        county_outline = dict(
            type='scatter',
            line=dict(width=0),
            name=lev,
            x=[0], y=[0],
            fill='toself',
            fillcolor=colors[levels.index(lev)],
            hoverinfo='none',
            mode='lines'
        )
        plot_data.append(county_outline)

    fig = dict(data=plot_data, layout=layout)

    return dcc.Graph(id='states_ranking_graph', figure=fig)

def congressmen_table_pretty(df_json):
    df = pd \
        .read_json(df_json, orient='split') \
        .sort_values(['numlegislatura', 'autorias'], ascending=False) \
        .drop_duplicates('idecadastro', keep="first")
    df = df.ix[:, [
        'autorias', 'nomeparlamentar', 'legendapartidoeleito', 'ufeleito', 'sexo', 'condicao'
    ]]

    df.sexo = df.sexo.map({'M': 'Masculino', 'F': 'Feminino'})

    df.columns = [
        'Proposições apresentadas', 'Deputado(a)', 'Último partido eleito', 'UF', 'Sexo', 'Condição'
    ]

    df_json = df.to_json(date_format='iso', orient='split')
    return df_json

def parties_infos(df_json):
    political_parties = pd.read_json(df_json, orient='split').set_index('idpartido')
    fig = tools.make_subplots(
        rows=1,
        cols=3,
        subplot_titles=['Proposições apresentadas', 'Número de autores', 'Razão apresentações por autores'],
        print_grid=False
    )

    fig['layout'].update(
        height=700,
        showlegend=False,
    )

    trace1 = go.Bar(
        x=political_parties.autorias.sort_values().values,
        y=political_parties.autorias.sort_values().index,
        orientation='h',
        marker=dict(
            color='#00B3E0'
        ),
    )

    trace2 = go.Bar(
        x=political_parties.autores.sort_values().values,
        y=political_parties.autores.sort_values().index,
        orientation='h',
        marker=dict(
            color='#00B3E0'
        ),
    )

    trace3 = go.Bar(
        x=political_parties.autoriasporautores.sort_values().values,
        y=political_parties.autoriasporautores.sort_values().index,
        orientation='h',
        marker=dict(
            color='#00B3E0'
        ),
    )

    fig['layout'].update(
        yaxis=dict(ticksuffix='  '),
        yaxis2=dict(ticksuffix='  '),
        yaxis3=dict(ticksuffix='  '),
    )

    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 2)
    fig.append_trace(trace3, 1, 3)

    return dcc.Graph(id='political_parties_graph', figure=fig)

def table_download(df_json):
    df = pd.read_json(df_json, orient='split')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

    return csv_string

def table_viz(df_json):
    df = pd.read_json(df_json, orient='split')
    df = df.drop_duplicates()
    return df.to_dict('records')
