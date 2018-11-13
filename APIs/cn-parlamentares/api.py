from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
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


class Parlamentares(Resource):
    def get(self, idecadastro):

	"""
        Retorna o(s) parlamentar(es) do período.

        :param idecadastro: id único do parlamentar ou 'lista'
        """

        conn = db_connect.connect()  # connect to database
        if idecadastro == 'lista':
            query = """
              SELECT DISTINCT
                idecadastro,
                nome_social
              FROM 
                dash_parlamentares.parlamentares
            """
        else:
            query = """
              SELECT 
                * 
              FROM 
                dash_parlamentares.parlamentares 
              WHERE
                idecadastro = {}
            """.format(idecadastro)

        data = conn.execute(query)
        result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
        return jsonify(result)


class Proposicoes(Resource):
    def get(self):

	"""
        Retorna detalhes das proposições apresentadas pelo parlamentar.

        :param idecadastro: id único do parlamentar
        """

        parser = reqparse.RequestParser()
        parser.add_argument('idautor', type=lambda x: [int(i) for i in x.split(',')])
        parser.add_argument('idproposicao', type=lambda x: [int(i) for i in x.split(',')])

        args = parser.parse_args()
        idecadastro, idproposicao = args['idautor'], args['idproposicao']

        conn = db_connect.connect()  # connect to database
        query = """
          SELECT
            *
          FROM
            dash_parlamentares.proposicoes
        """

        clauses = []
        if isinstance(idecadastro, list):
            clauses.append("idecadastro IN ({})".format(','.join(map(str, idecadastro))))

        if isinstance(idproposicao, list):
            clauses.append("idproposicao IN ({})".format(','.join(map(str, idproposicao))))

        if len(clauses) > 0:
            query += " WHERE " + " AND ".join(clauses)

        data = conn.execute(query)
        result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
        return jsonify(result)


class Orgaos(Resource):
    def get(self, idecadastro):

	"""
        Retorna os cargos exercidos pelo parlamentar nos órgãos da Câmara.

        :param idecadastro: id único do parlamentar
        """

        conn = db_connect.connect()  # connect to database
        query = """
          SELECT 
            * 
          FROM 
            dash_parlamentares.orgaos 
          WHERE
            idecadastro = {}
        """.format(idecadastro)
        data = conn.execute(query)
        result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
        return jsonify(result)


class Temas(Resource)
    def get(self, idecadastro):

        """
        Retorna o número de proposições apresentadas por tema pelo parlamentar.

	:param idecadastro: id único do parlamentar
        """

        conn = db_connect.connect()  # connect to database
        query = """
          SELECT 
            * 
          FROM 
            dash_parlamentares.parlamentares_temas
          WHERE
            idecadastro = {}
        """.format(idecadastro)
        data = conn.execute(query)
        result = {'data': [dict(zip(tuple(data.keys()), i)) for i in data.cursor]}
        return jsonify(result)


api.add_resource(Parlamentares, '/parlamentares/<idecadastro>')
api.add_resource(Proposicoes, '/proposicoes')
api.add_resource(Orgaos, '/orgaos/<idecadastro>')
api.add_resource(Temas, '/temas/<idecadastro>')

if __name__ == '__main__':
    app.run()
