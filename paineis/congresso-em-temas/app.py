# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import flask
import pandas as pd
import numpy as np
import geopandas as gp
from dash.dependencies import Input, Output

import methods
import styles
import utils

#import urllib
#import glob
#from collections import defaultdict
# noinspection PyDeprecation
#import os

# CONFIG APP
server = flask.Flask(__name__)
app = dash.Dash(name='thematic_painel', sharing=True, server=server, csrf_protect=False)

themes_file = pd.read_csv('themes.csv')
dropdown_options = [{'label': i['Tema'], 'value': i['Tema']}
                    for i in themes_file.to_dict('records')]

#def download_table(con, schema, table):
#    query = "SELECT * FROM {schema}.{table}".format(schema=schema, table=table)
#
#    df = pd.read_sql_query(query, con)
#    df_json = df.to_json(date_format='iso', orient='split')
#
#    return df_json


content = [

    # Header
    html.Div(
        id='header',
        children=[

            html.H1(
                'Câmara em temas',
                style={
                    'color': 'white',
                    'font-family': 'Lato, sans-serif',
                    'font-size': '50px',
                    'padding-top': 40,
                    'margin': '0px'
                }
            ),
        ],
        style={
            'background': '#2eb2ff',
            'height': 220,
            'margin-top': -10,
            'margin-left': -10,
            'margin-right': -10,
            'padding-left': '5%',
            'padding-right': '5%',
            'background-image': "url('https://raw.githubusercontent.com/AliferSales/viz-parallel/master/images/header-image-temas.png') "

        }
    ),

    html.Div(
        id='description',
        children=[
            html.P(
                "Bem-vindo(a) ao Painel Câmera em Temas. Neste painel apresentamos informações sobre as"
                "proposições que tramitam na Câmara dos Deputados, além dos autores, partidos e estados com "
                "maior autoria nas temáticas. Para fazer a sua análise, escolha o tema de interesse e defina "
                "o período da pesquisa. Os temas são definidos pela própria Câmera assim como a classificação "
                "das proposição O filtro de tema restringirá os resultados às proposições categorizadas com todos "
                "os temas escolhidos (ou seja, se você escolher 'Educação' e 'Tributação', serão consideradas as "
                "proposições classificadas com ambos os temas). Já o segundo filtro reunirá apenas as proposições "
                "que estiveram em fase de tramitação em algum momento do período escolhido."
            ),
            html.P(
                "Todos os dados são a partir de 2003 (52ª legislatura). Ou seja, apenas são consideradas "
                "proposições apresentadas a partir de 2003.",
            ),
            html.P('Boa Pesquisa!'),
            html.Br()
        ],
        style={
            'text-align': 'justify',
            'font-size': '15px',
            'color': '#007592',
            'padding-left': '5%',
            'padding-right': '5%',
            'padding-top': '20px',
        }
    ),

    html.Div(
        id='filters',
        children=[
            html.Table(
                children=[
                    html.Tr([
                        html.Td(
                            "Tema(s)",
                            style={
                                'width': 60,
                                'border': 'none',
                                'font-size': '15px',
                                'color': '#007592'
                            }
                        ),
                        html.Td(
                            dcc.Dropdown(
                                id='theme_filter',
                                options=dropdown_options,
                                value=['Arte e Cultura'],
                                multi=True,
                            ),
                            style={'border': 'none'}
                        )
                    ]),
                    html.Tr([
                        html.Td(
                            "Período",
                            style={
                                'border': 'none',
                                'font-size': '15px',
                                'color': '#007592'
                            }
                        ),
                        html.Td(
                            dcc.RangeSlider(
                                id='time_range_filter',
                                marks={i: i for i in range(2003, 2019)},
                                min=2003,
                                max=2018,
                                value=[2015, 2018]
                            ),
                            style={
                                'border': 'none',
                                'padding-right': '1%',
                                'padding-left': '1%'
                            }
                        )
                    ])
                ],
                style=styles.s_table()
            ),
            html.Br(),
            html.Br()
        ],
        style={
            'padding-left': '15%',
            'padding-right': '15%',
        }
    ),

    html.Div(
        id='returned_infos',
        children=[

            html.Div(
                id='propositions_infos',
                children=[

                    html.Div(
                        ['PROPOSIÇÕES'],
                        style=styles.s_section_title
                    ),

                    html.Div(
                        id='description_propositions',
                        children=[
                            html.P(
                                "Nesta seção, o painel apresenta o volume de projetos classificados com "
                                "os temas escolhidos que tramitaram no período escolhido",
                            ),
                            html.Br()
                        ],
                        style={
                            'text-align': 'justify',
                            'font-size': '15px',
                            'color': '#007592'
                        }
                    ),

                    html.Div(
                        id='propositions_big_numbers',
                        children=[

                            html.Table(
                                children=[
                                    html.Tr(
                                        children=[
                                            html.Td(
                                                children=[
                                                    html.Div(
                                                        id='propositions_number',
                                                        style={
                                                            'color': '#007592',
                                                            'font-size': '60px'
                                                        }
                                                    ),
                                                    html.Div(
                                                        'TOTAL',
                                                        style={
                                                            'font-size': '20px',
                                                            'color': '#515151'
                                                        }
                                                    )
                                                ],
                                                style={
                                                    'border': 'none',
                                                    'text-align': 'center',
                                                    'font-family': 'Lato, sans-serif',
                                                    'font-weight': 'bold'
                                                }
                                            ),
                                            html.Td(
                                                children=[
                                                    html.Div(
                                                        id='approved_number',
                                                        style={
                                                            'color': '#007592',
                                                            'font-size': '40px'
                                                        }
                                                    ),
                                                    html.Div(
                                                        'APROVADAS',
                                                        style={
                                                            'font-size': '16px',
                                                            'color': '#515151'
                                                        }
                                                    )
                                                ],
                                                style={
                                                    'border': 'none',
                                                    'text-align': 'center',
                                                    'font-family': 'Lato, sans-serif',
                                                    'font-weight': 'bold'
                                                }
                                            ),
                                            html.Td(
                                                children=[
                                                    html.Div(
                                                        id='processing_number',
                                                        style={
                                                            'color': '#007592',
                                                            'font-size': '40px'
                                                        }
                                                    ),
                                                    html.Div(
                                                        'EM TRAMITAÇÃO',
                                                        style={
                                                            'font-size': '16px',
                                                            'color': '#515151'
                                                        }
                                                    )
                                                ],
                                                style={
                                                    'border': 'none',
                                                    'text-align': 'center',
                                                    'font-family': 'Lato, sans-serif',
                                                    'font-weight': 'bold'
                                                }
                                            ),
                                            html.Td(
                                                children=[
                                                    html.Div(
                                                        id='archived_number',
                                                        style={
                                                            'color': '#007592',
                                                            'font-size': '40px'
                                                        }
                                                    ),
                                                    html.Div(
                                                        'ARQUIVADAS',
                                                        style={
                                                            'font-size': '16px',
                                                            'color': '#515151'
                                                        }
                                                    )
                                                ],
                                                style={
                                                    'border': 'none',
                                                    'text-align': 'center',
                                                    'font-family': 'Lato, sans-serif',
                                                    'font-weight': 'bold'
                                                }
                                            ),
                                        ]
                                    )
                                ],
                                style=styles.s_table()
                            ),
                            html.Hr()
                        ],
                    ),

                    html.Div(
                        id='types_of_propositions',
                        children=[
                            html.Table(
                                children=[
                                    html.Tr([

                                        html.Td(
                                            id='pec_number',
                                            style=styles.s_td(
                                                ('color', '#007592'),
                                                ('font-size', '30px'),
                                                ('border-left', 'solid 1px #E0E0E0')
                                            )
                                        ),

                                        html.Td(
                                            id='plp_number',
                                            style=styles.s_td(
                                                ('color', '#007592'),
                                                ('font-size', '30px')
                                            )
                                        ),

                                        html.Td(
                                            id='pl_number',
                                            style=styles.s_td(
                                                ('color', '#007592'),
                                                ('font-size', '30px')
                                            )
                                        ),
                                        html.Td(
                                            id='mpv_number',
                                            style=styles.s_td(
                                                ('color', '#007592'),
                                                ('font-size', '30px')
                                            )
                                        ),

                                        html.Td(
                                            id='plv_number',
                                            style=styles.s_td(
                                                ('color', '#007592'),
                                                ('font-size', '30px')
                                            )
                                        ),

                                        html.Td(
                                            id='pdc_number',
                                            style=styles.s_td(
                                                ('color', '#007592'),
                                                ('font-size', '30px')
                                            )
                                        )
                                    ]),
                                    html.Tr([
                                        html.Td(
                                            'PROPOSTAS DE EMENDA À CONSTITUÇÃO',
                                            style=styles.s_td(('border-left', 'solid 1px #E0E0E0'))
                                        ),

                                        html.Td(
                                            'PROJETOS DE LEI COMPLEMENTAR',
                                            style=styles.s_td()
                                        ),

                                        html.Td(
                                            'PROJETOS DE LEI',
                                            style=styles.s_td()
                                        ),

                                        html.Td(
                                            'MEDIDAS PROVISÓRIAS',
                                            style=styles.s_td()
                                        ),

                                        html.Td(
                                            'PROJETOS DE LEI DE CONVERSÃO',
                                            style=styles.s_td()
                                        ),

                                        html.Td(
                                            'PROJETOS DE DECRETO LEGISLATIVO',
                                            style=styles.s_td()
                                        )
                                    ]),
                                    html.Tr([
                                        html.Td(
                                            id='pec_disaggregated',
                                            style=styles.s_td(
                                                ('font-size', '15px'),
                                                ('border-left', 'solid 1px #E0E0E0')
                                            )
                                        ),

                                        html.Td(
                                            id='plp_disaggregated',
                                            style=styles.s_td(('font-size', '15px'))
                                        ),

                                        html.Td(
                                            id='pl_disaggregated',
                                            style=styles.s_td(('font-size', '15px'))
                                        ),

                                        html.Td(
                                            id='mpv_disaggregated',
                                            style=styles.s_td(('font-size', '15px'))
                                        ),

                                        html.Td(
                                            id='plv_disaggregated',
                                            style=styles.s_td(('font-size', '15px'))
                                        ),

                                        html.Td(
                                            id='pdc_disaggregated',
                                            style=styles.s_td(('font-size', '15px'))
                                        ),
                                    ])
                                ],
                                style=styles.s_table(('font-weight', 'bold'))
                            )
                        ],
                    ),

                    html.Hr(),

                    html.Div(
                        ['APRESENTADAS E APROVADAS NO PERÍODO'],
                        style=styles.s_subsection_title(35)
                    ),

                    html.Div(
                        id='description_approved_presented',
                        children=[
                            html.P(
                                "Quantas proposições foram apresentadas e aprovadas por ano",
                            ),
                            html.Br()
                        ],
                        style={
                            'text-align': 'justify',
                            'font-size': '15px',
                            'color': '#007592'
                        }
                    ),

                    html.Div(id='approved_presented_propositions'),

                    html.Hr(),

                    html.Div(
                        ['LISTA DE PROPOSIÇÕES'],
                        style=styles.s_subsection_title()
                    ),

                    html.Div(
                        id='propositions_table_div',
                        children=[
                            dt.DataTable(
                                id='propositions_table_viz',
                                rows=[{}],
                                columns=[
                                    'Apresentação', 'Proposição', 'Tema(s)', 'Autor', 'Partido Eleito',
                                    'UF', 'Última tramitação', 'Situação', 'Descrição da Situação'
                                ]
                            ),
                            html.A(
                                'Download Data',
                                id='propositions_table_download',
                                download="propositions_data.csv",
                                href="",
                                target="_blank"
                            )
                        ]
                    )
                ]
            ),

            html.Br(),

            html.Div(
                id='congressmen_infos',
                children=[

                    html.Div(
                        ['PARLAMENTARES'],
                        style=styles.s_section_title
                    ),

                    html.Div(
                        id='description_congressmen',
                        children=[
                            html.P(
                                "Nesta seção, é possível identificar o total de proposições classificadas com "
                                "os temas escolhidos que foram apresentadas por deputadas(os), partidos e "
                                "bancadas estaduais",
                            ),
                            html.Br()
                        ],
                        style={
                            'text-align': 'justify',
                            'font-size': '15px',
                            'color': '#007592'
                        }
                    ),

                    html.Table(
                        html.Tr([
                            html.Td(
                                id='congressmen_ranking',
                                style={'width': '29%'}
                            ),
                            html.Td(
                                id='parties_ranking',
                                style={'width': '29%'}
                            ),
                            html.Td(
                                id='states_ranking',
                                style={'width': '42%'}
                            ),
                        ]),
                        style=styles.s_table()
                    ),

                    html.Div(
                        ['AUTORIAS POR PARTIDOS'],
                        style=styles.s_subsection_title()
                    ),

                    html.Div(
                        id='description_parties_graph',
                        children=[
                            html.P(
                                "Esta seção traz o ranking de partidos por número de apresentações, à esquerda; "
                                "o ranking de partidos por número de parlamentares que apresentaram pelo menos "
                                "uma proposição classificada com os temas escolhidos, ao centro; e, à direita, o "
                                "ranking dos partidos pelo número de apresentações sobre o número de candidatos que "
                                "apresentaram pelo menos uma proposição nos temas escolhidos.",
                            ),
                            html.Br()
                        ],
                        style={
                            'text-align': 'justify',
                            'font-size': '15px',
                            'color': '#007592'
                        }
                    ),

                    html.Div(
                        id='parties_table_div',
                        children=[
                            # dt.DataTable(
                            #     id='parties_table_viz',
                            #     rows=[{}],
                            #     columns=[
                            #         'Sigla', 'Proposições apresentadas', 'Total de autores',
                            #         'Relação proposições por autores'
                            #     ]
                            # )
                        ]
                    ),
                    html.A(
                        'Download Data',
                        id='parties_table_download',
                        download="political_parties_data.csv",
                        href="",
                        target="_blank"
                    )
                ]),

            html.Div(
                ['LISTA DE PARLAMENTARES'],
                style=styles.s_subsection_title()
            ),

            html.Div(
                id='congressmen_table_div',
                children=[
                    dt.DataTable(
                        id='congressmen_table_viz',
                        rows=[{}],
                        columns=[
                            'Proposições apresentadas', 'Deputado(a)', 'Último partido eleito', 'UF', 'Condição'
                        ]
                    ),
                    html.A(
                        'Download Data',
                        id='congressmen_table_download',
                        download="congressmen_data.csv",
                        href="",
                        target="_blank"
                    )
                ]
            ),

        ],
        style={
            'padding-left': '5%',
            'padding-right': '5%'
        }
    ),

    html.Div(
        id='footer',
        children=[
            html.Table(
                html.Tr([
                    html.Td(style={'padding': 0, 'border': 'none'}),
                    # Logo CTS
                    html.Td(
                        html.P([
                            'Desenvolvido em 2018 | v0.1'
                        ],
                            style={
                                'align': 'center',
                                'color': '#FFFFFF',
                                'font-family': 'Lato, sans-serif',
                                'text-align': 'center',
                                'font-weight': 'bold'
                            }
                        ),
                        style={'padding': 0, 'border': 'none'}
                    ),
                    html.Td([
                        # Github link
                        # html.A(
                        #     utils.html_img(
                        #         'images/icone-github-branco.png',
                        #         style={'width': '45px', 'padding-right': '5%'}
                        #     ),
                        #     href="https://github.com/CTS-FGV",
                        #     target="_blank"
                        # ),
                        # # Facebook link
                        # html.A(
                        #     utils.html_img(
                        #         'images/icone-facebook-branco.png',
                        #         style={'width': '45px', 'padding-right': '15%'}
                        #     ),
                        #     href="https://www.facebook.com/ctsfgv",
                        #     target="_blank"
                        # )
                    ],
                        style={'padding': 0, 'border': 'none', 'text-align': 'right'}
                    )
                ]),
                style=s_table(('height', '120'))
            )
        ],
        style={"background": '#297DAD', 'height': 120, 'margin': -10, 'margin-top': 30}
    ),

    # Hidden divs inside the app that stores the intermediate value


    html.Div(id='congressmen_table_pretty', style={'display': 'none'}),
    html.Div(id='propositions_table_pretty', style={'display': 'none'}),
    html.Div(id='parties_table', style={'display': 'none'}),
    html.Div(id='congressmen_table', style={'display': 'none'}),
    html.Div(id='propositions_table', style={'display': 'none'})

]

app.layout = html.Div(content)

######################## CALLBACKS #######################
##########################################################


INPUT = dash.dependencies.Input
OUTPUT = dash.dependencies.Output


######################## FILTERS #########################
##########################################################


@app.callback(
    OUTPUT('propositions_table', 'children'),
    [INPUT('theme_filter', 'value'),
     INPUT('time_range_filter', 'value')])
def propositions_filter(themes_list, years_range):
    return methods.propositions_filter(themes_list, years_range)

@app.callback(OUTPUT('congressmen_table', 'children'),
	     [INPUT('theme_filter', 'value'),
	     INPUT('time_range_filter', 'value')])
def congressmen_filter(themes_list, years_range):
    return methods.congressmen_filter(themes_list, years_range)

@app.callback(OUTPUT('parties_table', 'children'),
	     [INPUT('theme_filter', 'value'),
	     INPUT('time_range_filter', 'value')])
def political_parties_filter(themes_list, years_range):
    return methods.political_parties_filter(themes_list, years_range)

################### PROPOSITIONS SECTION #################
##########################################################

################## PROPOSITIONS NUMBERS ###################

@app.callback(OUTPUT('propositions_number', 'children'), [INPUT('propositions_table', 'children')])
def propositions_amount(df_json):
    return propositions_status_amount(df_json)

@app.callback(OUTPUT('approved_number', 'children'), [INPUT('propositions_table', 'children')])
def approved_amount(df_json):
    status = 'Aprovada'
    return propositions_status_amount(df_json, status)


@app.callback(OUTPUT('processing_number', 'children'), [INPUT('propositions_table', 'children')])
def processing_amount(df_json):
   status = 'Em tramitação'
    return propositions_status_amount(df_json, status)


@app.callback(OUTPUT('archived_number', 'children'), [INPUT('propositions_table', 'children')])
def archived_amount(df_json):
    status = 'Arquivada'
    return propositions_status_amount(df_json, status)


################## TYPES OF PROPOSITIONS ###################

@app.callback(OUTPUT('pec_number', 'children'), [INPUT('propositions_table', 'children')])
def pec_amount(df_json):
    type = 'PEC '
    return methods.propositions_type_amount(df_json, type)

@app.callback(OUTPUT('pl_number', 'children'), [INPUT('propositions_table', 'children')])
def pl_amount(df_json):
    type = 'PL '
    return methods.propositions_type_amount(df_json, type)

@app.callback(OUTPUT('mpv_number', 'children'), [INPUT('propositions_table', 'children')])
def mpv_amount(df_json):
    type = 'MPV '
    return methods.propositions_type_amount(df_json, type)

@app.callback(OUTPUT('plp_number', 'children'), [INPUT('propositions_table', 'children')])
def plp_amount(df_json):
    type = 'PLP '
    return methods.propositions_type_amount(df_json, type)

@app.callback(OUTPUT('plv_number', 'children'), [INPUT('propositions_table', 'children')])
def plv_amount(df_json):
    type = 'PLV '
    return methods.propositions_type_amount(df_json, type)

@app.callback(OUTPUT('pdc_number', 'children'), [INPUT('propositions_table', 'children')])
def pdc_amount(df_json):
    type = 'PDC '
    return methods.propositions_type_amount(df_json, type)

################ PROPOSITIONS TYPES NUMBERS #################

@app.callback(OUTPUT('pec_disaggregated', 'children'), [INPUT('propositions_table', 'children')])
def pec_disaggregated(df_json):
    type = 'PEC '
    return methods.propositions_type_disaggregated(df_json, type)


@app.callback(OUTPUT('pl_disaggregated', 'children'), [INPUT('propositions_table', 'children')])
def pl_disaggregated(df_json):
    type = 'PL '
    return methods.propositions_type_disaggregated(df_json, type)

@app.callback(OUTPUT('mpv_disaggregated', 'children'), [INPUT('propositions_table', 'children')])
def mpv_disaggregated(df_json):
    type = 'MPV '
    return methods.propositions_type_disaggregated(df_json, type)

@app.callback(OUTPUT('plp_disaggregated', 'children'), [INPUT('propositions_table', 'children')])
def plp_disaggregated(df_json):
    type = 'PLP '
    return methods.propositions_type_disaggregated(df_json, type)

@app.callback(OUTPUT('plv_disaggregated', 'children'), [INPUT('propositions_table', 'children')])
def plv_disaggregated(df_json):
    type = 'PLV '
    return methods.propositions_type_disaggregated(df_json, type)

@app.callback(OUTPUT('pdc_disaggregated', 'children'), [INPUT('propositions_table', 'children')])
def pdc_disaggregated(df_json):
    type = 'PDC '
    return methods.propositions_type_disaggregated(df_json, type)

########## APPROVED AND PRESENTED PROPOSITIONS ############

@app.callback(OUTPUT('approved_presented_propositions', 'children'),
              [INPUT('propositions_table', 'children'),
               INPUT('time_range_filter', 'value')])
def approved_presented_graph(df_json, years_range):
    return methods.approved_presented_graph(df_json)

################# PROPOSITIONS TABLE ###################

@app.callback(OUTPUT('propositions_table_pretty', 'children'),
              [INPUT('propositions_table', 'children'),
               INPUT('congressmen_table', 'children')])
def propositions_table_pretty(propositions_json, congressmen_json):
    return methods.propositions_table_pretty(df_json)

@app.callback(OUTPUT('propositions_table_viz', 'rows'),[INPUT('propositions_table_pretty', 'children')])
def propositions_table_viz(df_json):
    return methods.table_viz(df_json)

@app.callback(OUTPUT('propositions_table_download', 'href'), [INPUT('propositions_table_pretty', 'children')])
def propositions_table_download(df_json):
    return methods.table_download(df_json)

################### CONGRESSMEN SECTION ##################
##########################################################


@app.callback(OUTPUT('congressmen_ranking', 'children'), [INPUT('congressmen_table', 'children')])
def congressmen_ranking(congressmen_json):
    return methods.congressmen_ranking(df_json)

@app.callback(OUTPUT('parties_ranking', 'children'), [INPUT('parties_table', 'children')])
def political_parties_ranking(df_json):
    return methods.political_parties_ranking(df_json)

@app.callback(OUTPUT('states_ranking', 'children'), [INPUT('congressmen_table', 'children')])
def states_ranking(df_json):
    return methods.states_ranking(df_json)


################# PROPOSITIONS TABLE ###################

@app.callback(OUTPUT('congressmen_table_pretty', 'children'), [INPUT('congressmen_table', 'children')])
def congressmen_table_pretty(df_json):
    return methods.congressmen_table_pretty(df_json)

@app.callback(OUTPUT('congressmen_table_viz', 'rows'), [INPUT('congressmen_table_pretty', 'children')])
def congressmen_table_viz(df_json):
    # não tinha drop_duplicates!
    return methods.table_viz(df_json)

@app.callback(OUTPUT('congressmen_table_download', 'href'), [INPUT('congressmen_table_pretty', 'children')])
def congressmen_table_download(df_json):
    return methods.table_download(df_json)
###

# @app.callback(OUTPUT('parties_table_viz', 'rows'), [INPUT('parties_table', 'children')])
# def political_parties_table(df_json):
#     df = pd.read_json(df_json, orient='split')
#     df = df.ix[:, [
#         'autorias', 'idpartido', 'autores', 'autoriasporautores'
#     ]]
#
#     df.autoriasporautores = df.autoriasporautores.apply(lambda x: '{0:.2f}'.format(x))
#
#     df.columns = [
#         'Proposições apresentadas', 'Sigla', 'Total de autores', 'Relação proposições por autores'
#     ]
#
#     return df.to_dict('records')


@app.callback(OUTPUT('parties_table_div', 'children'), [INPUT('parties_table', 'children')])
def parties_infos(df_json):
    return methods.parties_infos(df_json)

@app.callback(OUTPUT('parties_table_download', 'href'), [INPUT('parties_table', 'children')])
def congressmen_table_download(df_json):
    return methods.table_download(df_json)
########################################################
########################################################
########################################################

# Append css
app.css.append_css({"external_url": "https://codepen.io/alifersales/pen/wmyGgO.css"})

if __name__ == '__main__':
    app.run_server()
