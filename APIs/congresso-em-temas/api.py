from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
from datetime import datetime
import yaml
import sys
from pathlib import Path 

current_path = Path().resolve()
abs_path = str(current_path.parent)
sys.path.append(abs_path)

server = yaml.load(open(str(current_path.parent.parent / 'dbconfig.yaml'))
db_connect = create_engine(server['db_dashes'])

app = Flask(__name__)
api = Api(app)

class Proposicoes(Resource):
    def get(self, tema, periodo):
	
	"""
	Retorna as proposições do(s) tema(s) escolhido.
	
	:param tema: string do tema ou list com strings
	:param periodo: list com ano inicial e final

	:return: str(json)
	"""

	conn = db_connect.connet()  # connect to database

	if isinstance(tema, list):
	    tema = '|'.join(map(str, tema))

	query = """
	  SELECT
 	    *
    	  FROM 
  	    dash_temas.proposicoes
	  WHERE 
	    tema SIMILAR TO '(%%{tema}%%)'
	  AND
	    (EXTRACT(YEAR FROM dataapresentacao) <= {ano1}
              AND (descricao_situacao = 'Em Tramitação'
	        OR (descricao_situacao != 'Em Tramitação'
		  AND EXTRACT(YEAR FROM data_ultima_tramitacao) >= {ano0}
		)
	      )
            )""".format(tema, periodo[1], periodo[0])

	data = conn.execute(query)
        result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
        return jsonify(result)


class Parlamentares(Resource):
    def get(self, tema, proposicoes):

	"""
	Retorna os parlamentares com proposições apresentadas sobre o(s) tema(s) no período.

	:param tema: string ou lista de strings com temas
	:param periodo: lista com ano inicial e final para busca

	:return: str(json)
	"""

	conn = db_connect.connect()  # connect to database

	# filtra as proposições do tema e período
        if isinstance(tema, list):
            tema = '|'.join(map(str, tema))

        query = """
          SELECT
            *
          FROM 
            dash_temas.proposicoes
          WHERE 
            tema SIMILAR TO '(%%{tema}%%)'
          AND
            (EXTRACT(YEAR FROM dataapresentacao) <= {ano1}
              AND (descricao_situacao = 'Em Tramitação'
                OR (descricao_situacao != 'Em Tramitação'
                  AND EXTRACT(YEAR FROM data_ultima_tramitacao) >= {ano0}
                )
              )
            )""".format(tema, periodo[1], periodo[0])

	proposicoes = conn.execute(query)
	proposicoes.idecadastro = np.nan_to_num(proposicoes.idecadastro).astype(int)

	# calcula as autorias por deputado
	autorias = pd.DataFrame(proposicoes.idecadastro.value_counts())
	autorias.columns = ['autorias']

	# filtra deputados em exercício no período
	ano_atual = datetime.now().year
	anos_legs = {ano: int((ano - 2003) / 4 + 52) for year in range(2003, ano_atual)}

	query2 = """
	    SELECT
        	*
   	    FROM
        	dash_temas.deputados
    	    WHERE
       		numlegislatura BETWEEN {leg0} AND {leg1}
    	    ORDER BY
        	numlegislatura DESC;
    	    """.format(leg0=anos_legs[periodo[0]], leg1=anos_legs[periodo[1]])

	parlamentares = pd.read_sql_query(query2, con)
	parlamentares = parlamentares.merge(autorias, left_on='idecadastro', right_index=True, how='left')
	df_json = parlamentares.to_json(date_format='iso', orient='split')

	#result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
	#return jsonify(result)

	return df_json

class Partidos(Resource):
    def get(self, tema, periodo):
	"""
        Retorna os partidos com proposições apresentadas sobre o(s) tema(s) no período

        :param tema: string ou lista de strings com temas
        :param periodo: lista com ano inicial e final para busca

        :return: str(json)
        """

	conn = db_connect.connect()  # connect to database

        # filtra as proposições do tema e período
        if isinstance(tema, list):
            tema = '|'.join(map(str, tema))

        query = """
          SELECT
            *
          FROM 
            dash_temas.proposicoes
          WHERE 
            tema SIMILAR TO '(%%{tema}%%)'
          AND
            (EXTRACT(YEAR FROM dataapresentacao) <= {ano1}
              AND (descricao_situacao = 'Em Tramitação'
                OR (descricao_situacao != 'Em Tramitação'
                  AND EXTRACT(YEAR FROM data_ultima_tramitacao) >= {ano0}
                )
              )
            )""".format(tema, periodo[1], periodo[0])

        proposicoes = conn.execute(query)
        proposicoes.idecadastro = np.nan_to_num(proposicoes.idecadastro).astype(int)

        # calcula as autorias por deputado
        autorias = pd.DataFrame(proposicoes.idecadastro.value_counts())
        autorias.columns = ['autorias']

        # filtra deputados em exercício no período
        ano_atual = datetime.now().year
        anos_legs = {ano: int((ano - 2003) / 4 + 52) for year in range(2003, ano_atual)}


	query2 = """
            SELECT
                *
            FROM
                dash_temas.deputados
            WHERE
                numlegislatura BETWEEN {leg0} AND {leg1}
            ORDER BY
                numlegislatura DESC;
            """.format(leg0=anos_legs[periodo[0]], leg1=anos_legs[periodo[1]])

        parlamentares = pd.read_sql_query(query2, con)
        parlamentares = parlamentares.merge(autorias, left_on='idecadastro', right_index=True, how='left')
        #df_json = parlamentares.to_json(date_format='iso', orient='split')

        #result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
        #return jsonify(result)

        # filtra partidos políticos

	parlamentares = parlamentares.rename(columns={'legendapartidoeleito': 'idpartido'}) \
            			.sort_values('numlegislatura', ascending=False) \
            			.drop_duplicates(['idecadastro', 'idpartido'], keep='first')


	nomes = pd.read_sql_query("SELECT * FROM dash_temas.partidos", con)

	autorias = parlamentares[['idpartido', 'autorias']] \
        		.dropna() \
        		.groupby(['idpartido']) \
        		.agg({'idpartido': 'count', 'autorias': 'sum'}) \
        		.rename(columns={'idpartido': 'autores'})

	df = autorias.merge(names, left_index=True, right_on='idpartido', how='left') \
        	.sort_values('autorias', ascending=False)

	df['autoriasporautores'] = df['autorias'] / df['autores']
	df_json = df.to_json(date_format='iso', orient='split')

	return df_json


api.add_resouce(Proposicoes, 'proposicoes/<tema>', 'proposicoes/<periodo>')
api.add_resource(Parlamentares, '/parlamentares/<tema>', 'parlamentares/<periodo>')
api.add_resource(Partidos, 'partidos/<tema>', 'partidos/<periodo>')


if __name__ == '__main__':
    app.run()
