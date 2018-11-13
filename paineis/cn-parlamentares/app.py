# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import flask
import numpy as np
import pandas as pd
import requests
from dash.dependencies import Input, Output

import methods
import styles
import utils

# CONFIG APP
server = flask.Flask(__name__)
app = dash.Dash(name='congressmen_panel', sharing=True, server=server, csrf_protect=False)

# GET CONGRESSMEN LIST

list_congressmen = requests.get('http://35.192.83.177:5005/parlamentares/lista').json()['data']
list_congressmen = [{'value': dic['idecadastro'], 'label': dic['nome_social']}
                    for dic in list_congressmen]

content = [

    # Header
    html.Div(
        id='header',
        children=[

            html.H1(
                'Perfil Parlamentar',
                style=styles.title1()
            ),

        ],
        style=styles.header()
    ),

    html.Div(
        id='description',
        children=[
            html.P(
                "Bem-vinda(o) ao Painel do Perfil Parlamentar. Para fazer a sua análise, escolha a/o parlamentar de "
                "interesse para obter informações sobre sua atividade parlamentar. Os resultados reúnem informações "
                "sobre as proposições apresentadas, comissões de participação e temas de maior autoria. Apenas são "
                "consideradas as proposições que têm o poder de alterar o ordenamento jurídico, sendo elas PEC, PLP, "
                "PL, MPV, PLV e PDC.",
            ),
            html.P(
                "Algumas informações importantes: Todos os dados são a partir de 2003 (52ª legislatura). Ou seja, "
                "apenas são consideradas proposições apresentadas a partir de 2003. O número de mandatos também só é "
                "contado a partir de 2003. Finalmente, os parlamentares disponíveis são apenas os que exerceram "
                "mandato na legislatura atual (55ª de 2015 a 2018).",
            ),
            html.P('Boa Pesquisa!'),
            html.Br()
        ],
        style=styles.text1(
            ('padding-left', '5%'),
            ('padding-right', '5%'),
            ('padding-top', '20px')
        )
    ),

    html.Div(
        id='filters',
        children=[
            html.Table(
                children=[
                    html.Tr([
                        html.Td(
                            "Parlamentar",
                            style=styles.td_filter()
                        ),
                        html.Td(
                            dcc.Dropdown(
                                id='congressmen_filter',
                                options=list_congressmen
                            ),
                            style=styles.td(('padding', 'none'))
                        )
                    ])
                ],
                style=styles.table()
            ),
        ],
        style=styles.filter()
    ),

    html.Div(
        id='row 1',
        children=[

            html.Div(
                id='congressmam_profile_section',
                children=[

                    html.Hr(),

                    # html.Div(
                    #     ['Perfil parlamentar'],
                    #     style=styles.section_title()
                    # ),
                    #
                    # html.Div(
                    #     children=[
                    #         html.P(
                    #             "Nesta seção, o painel apresenta [o volume de projetos analisados por parlamentares sobre o tema no período escolhido]",
                    #         ),
                    #         html.Br()
                    #     ],
                    #     style=styles.text1()
                    # ),

                    html.Div(id='congressmam_profile')
                ]
            )

        ],
        style=styles.body()
    ),

    html.Div(
        id='row 2',
        children=[

            html.Table(
                html.Tr([
                    html.Td(
                        id='committees_section',
                        children=[
                            html.Div(
                                ['Histórico de Comissões'],
                                style=styles.subsection_title(40, ('padding', 0))
                            ),
                            dt.DataTable(
                                id='committees_table_viz',
                                rows=[{}],
                                columns=['Orgão', 'Nome', 'Cargo', 'Entrada', 'Saída']
                            ),
                            html.A(
                                'Download Data',
                                id='committees_table_download',
                                download="orgaos.csv",
                                href="",
                                target="_blank"
                            )
                        ],
                        style=styles.td_body()
                    ),
                    html.Td(
                        id='themes_section',
                        children=[
                            html.Div(
                                ['Temas mais apresentados'],
                                style=styles.subsection_title(40, ('padding', 0))
                            ),
                            # html.Div(
                            #     children=[
                            #         html.P(
                            #             "Número de proposições mais apresentadas pelos 5 temas mais apresentados pelo autor.",
                            #         ),
                            #         html.Br()
                            #     ],
                            #     style=styles.text1()
                            # ),
                            html.Div(id='themes_graph')
                        ],
                        style=styles.td_body()
                    )
                ]),
                style=styles.table()
            )

        ],
        style=styles.body()
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
                style=styles.table(('height', '120'))
            )
        ],
        style={"background": '#297DAD', 'height': 120, 'margin': -10, 'margin-top': 30}
    ),

    # Hidden divs inside the app that stores the intermediate value

    html.Div(id='committees_table_pretty', style={'display': 'none'})

]
app.layout = html.Div(content)

######################## CALLBACKS #######################
##########################################################

INPUT = dash.dependencies.Input
OUTPUT = dash.dependencies.Output

##########################################################

@app.callback(OUTPUT('congressmam_profile', 'children'), [INPUT('congressmen_filter', 'value')])
def congressman_info(idecadastro):
    return methods.congressman_info(idecadastro)


@app.callback(OUTPUT('committees_table_pretty', 'children'), [INPUT('congressmen_filter', 'value')])
def committees_table_pretty(idecadastro):
    return methods.committees_table(idecadastro)


@app.callback(OUTPUT('committees_table_viz', 'rows'), [INPUT('committees_table_pretty', 'children')])
def committees_table_viz(df_json):
    df = pd.read_json(df_json, orient='split')
    return df.to_dict('records')


@app.callback(OUTPUT('committees_table_download', 'href'), [INPUT('committees_table_pretty', 'children')])
def committees_table_download(df_json):
    return methods.table_download(df_json)


@app.callback(OUTPUT('themes_graph', 'children'), [INPUT('congressmen_filter', 'value')])
def themes_graph(idecadastro):
    return methods.themes_graph(idecadastro)



########################################################
########################################################
########################################################

# Append css
app.css.append_css({"external_url": "https://codepen.io/alifersales/pen/wmyGgO.css"})

if __name__ == '__main__':
    app.run_server(port=5002)
