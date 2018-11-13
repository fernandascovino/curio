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


def congressman_info(idecadastro):
    if not idecadastro: return None

    def plural(n):
        if n > 1: return 's'
        return ''

    data = requests.get('http://35.192.83.177:5005/parlamentares/{}'.format(idecadastro)).json()['data'][0]
    mandatos = data['mandatos_desde2003']

    general_infos = [
        html.Div(
            html.A(
                data['nome_social'],
                href='http://www.camara.leg.br/Internet/Deputado/dep_Detalhe.asp?id={}'.format(idecadastro),
                target='_blank',
                style={'text-decoration': 'none', 'color': 'inherit'}
            ),
            style=styles.profile_name()
        ),
        html.Div('{} - {} | {}'.format(data['partido_atual'], data['uf_eleicao'], data['situacao_exercicio'])),
        html.Div('{} Mandato{}'.format(mandatos, plural(mandatos))),
        html.Div('Fidelidade Partidária: {0:.2f}%'.format(data['fidelidade']*100)),
        html.Div('{0:,.0f} Votos'.format(data['total_votos'])),
        html.Div('{0:.2f}% dos votos do partido no estado'.format(data['percent_party']*100)),
    ]

    content = [
        html.Td(
            utils.html_img(
                data['url_foto'],
                local=False,
                style={'height': 170}
            ),
            style=styles.td()
        ),
        html.Td(
            general_infos,
            style=styles.td(
                ('padding-left', '10'),
                ('font-family', 'Lato, sans-serif'),
                ('color', '#515151'),
                ('font-size', '18px'),
                ('width', '33%')
            )
        ),
        html.Td([
            html.Div(
                html.Table([
                    html.Tr([
                        html.Td(
                            data['apresentacoes'],
                            style=styles.td_big_number()
                        ),
                        html.Td([
                            html.Div('PROPOSIÇÕES'),
                            html.Div('APRESENTADAS')
                        ],
                            style=styles.td_text_big_number()
                        )
                    ]),
                    html.Tr([
                        html.Td(
                            '{0:.1f}'.format(data['media_apresentacoes']),
                            style=styles.td_big_number(('font-size', 40))
                        ),
                        html.Td([
                            html.Div('MÉDIA DE APRESENTAÇÕES'),
                            html.Div('POR PARLAMENTAR')
                        ],
                            style=styles.td_text_big_number(('font-size', 14))
                        )
                    ])
                ])

            )
        ],
            style=styles.td(('width', '27%'))
        ),
        html.Td([
            html.Div(
                html.Table([
                    html.Tr([
                        html.Td(
                            '{0:.1f}%'.format(data['taxa_sucesso'] * 100),
                            style=styles.td_big_number()
                        ),
                        html.Td([
                            html.Div('PROPOSIÇÕES'),
                            html.Div('APROVADAS')
                        ],
                            style=styles.td_text_big_number()
                        )
                    ]),
                    html.Tr([
                        html.Td(
                            '{0:.1f}%'.format(data['media_taxa_sucesso'] * 100),
                            style=styles.td_big_number(('font-size', 40))
                        ),
                        html.Td([
                            html.Div('MÉDIA DE APROVAÇÕES'),
                            html.Div('NA CÂMARA')
                        ],
                            style=styles.td_text_big_number(('font-size', 14))
                        )
                    ])
                ],
                    style=styles.table()
                )

            )
        ],
            style=styles.td(('width', '30%'))
        )
    ]

    table = html.Table(
        html.Tr(content)
    )
    return table


def committees_table(idecadastro):
    data = requests.get('http://35.192.83.177:5005/orgaos/{}'.format(idecadastro)).json()['data']
    df = pd.DataFrame(data)

    df.datainicio = pd.to_datetime(df.datainicio).dt.date
    df.datafim = pd.to_datetime(df.datafim).dt.date.replace(np.nan, 'presente')

    df.datainicio = df.datainicio.apply(utils.date_to_str_pretty)
    df.datafim = df.datafim.apply(utils.date_to_str_pretty)

    df = df.loc[:, ['siglaorgao', 'nomeorgao', 'nomepapel', 'datainicio', 'datafim']]
    df.columns = ['Orgão', 'Nome', 'Cargo', 'Entrada', 'Saída']
    df = df.sort_values('Entrada', ascending=0)

    df_json = df.to_json(date_format='iso', orient='split')
    return df_json


def table_download(df_json):
    df = pd.read_json(df_json, orient='split')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


def themes_graph(idecadastro):
    data = requests.get('http://35.192.83.177:5005/temas/{}'.format(idecadastro)).json()
    if 'data' not in data:
        #     return None
        print('error')
    data = data['data'][0]
    data.pop('idecadastro')
    data.pop('index')

    sorted_data = sorted(data.items(), key=operator.itemgetter(1))

    top5 = [i for i in sorted_data if i[1] != 0][-5:]
    # top5.extend([(' ' * i, 0) for i in range(5 - len(top5))])

    others = [i for i in sorted_data if i[1] != 0][:-5]
    full = [('Outros', sum([i[1] for i in others]))] + top5
    full = tuple(zip(*full))

    themes, amount = full

    data = go.Bar(
        orientation='h',
        y=themes,
        x=amount,
        # text=['{}<br>{} proposições'.format(i,j) for i,j in zip(themes,amount)],
        text=themes,
        textposition='outside',
        marker={'color': "#00B3E0"}
    )

    annotations = []
    shapes = []
    for i in range(len(amount)):
        v = amount[i]
        if v > 10:
            l = 5
        elif v > 2:
            l = 2
        else:
            l = 0.5

        if v > 200:
            text = '{} - {}'.format(themes[i], v)
            annotations.append(dict(
                y=i,
                x=240 - len(text),
                text=text,
                showarrow=False,
                font=dict(
                    color="white",
                    size=12,
                    family='Lato, sans-serif'
                ),
            ))
            annotations.append(dict(
                y=i + .55,
                x=240 - len(text),
                text='CONTINUA -->>    ',
                showarrow=False,
                font=dict(
                    color="rgb(170, 170, 170)",
                    size=12,
                    family='Lato, sans-serif'
                ),
            ))
            shapes = [{
                'type': 'line',
                'x0': 250, 'y0': -.5,
                'x1': 250, 'y1': 6,
                'line': {
                    'color': 'rgb(170, 170, 170)',
                    'width': 3,
                    'dash': 'dot'
                }
            }]
        else:
            annotations.append(dict(
                y=i,
                x=v - l,
                text=str(v),
                showarrow=False,
                font=dict(
                    color="white",
                    size=12,
                    family='Lato, sans-serif'
                ),
            ))

    layout = go.Layout(
        margin=go.Margin(
            l=20,
            t=10,
            pad=0
        ),
        xaxis=dict(
            ticks='',
            range=[0, 250],
            tickfont=dict(
                size=10,
                family='Lato, sans-serif'
            ),
            zeroline=False,
            title='Quantidade'
        ),
        yaxis=dict(
            ticks='',
            showticklabels=False,
            title='Temas'
        ),
        annotations=annotations,
        shapes=shapes
    )

    fig = go.Figure(data=[data], layout=layout)

    return dcc.Graph(id='plotly_themes', figure=fig)