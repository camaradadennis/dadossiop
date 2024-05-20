"""
Este módulo oferece um cliente para consultas ao endpoint SPARQL do SIOP,
Sistema de Integrado de Planejamento e Orçamento, vinculado à Secretaria de
Orçamento do Ministério do Planejamento.

Para isso, ele expõe a classe DadosSIOP(), que se conecta ao
endpoint do SIOP e envia as queries no formato SPARQL.

O módulo pode ser utilizado em algum código python:
    from dadossiop import DadosSIOP

    dados = DadosSIOP()
    r = dados.query(query_string)

Ou como um script standalone:
    python dadossiop.py <arquivo_contendo_a_query>

No segundo caso, o output será escrito em stdout e pode ser direcionado a um
arquivo usando lógica padrão de direcionamento no terminal. Ex.
    python dadossiop.py arquivo_contendo_a_query > output.csv

Documentação sobre o SIOP pode ser encontrada em
https://orcamento.dados.gov.br
"""

from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

import ssl
from urllib.request import HTTPSHandler, OpenerDirector, install_opener

import os.path

# Instala o certificado SSL do SIOP no contexto do urllib
siop_ssl_context = ssl.create_default_context(
    cafile=os.path.dirname(__file__) + '/siop-planejamento-gov-br.pem')
opener = OpenerDirector()
opener.add_handler(HTTPSHandler(context=siop_ssl_context))
install_opener(opener)

def _recode(term):
    """função auxiliar que lida com datatypes recebidos de queries.

    Recebe um rdflib.term e retorna um tipo nativo do python. Adicionalmente,
    caso o tipo seja string, muda o encoding para utf-8.
    """

    t = term.toPython()
    if isinstance(t, str):
        t = t.encode('latin-1').decode('utf-8')
    return t

class QueryResult:
    """Wrapper sobre a classe Result do rdflib.

    Sua função aqui é basicamente prover os métodos save() e to_frame()
    que respectivamente salvam o resultado em um arquivo e transformam
    o resultado em um pandas DataFrame.

    to_frame() só irá funcionar se a biblioteca Pandas estiver instalada
    no sistema.

    Também, QueryResult utiliza a função auxiliar _recode() para trazer o
    resultado para UTF-8.

    QueryResult foi pensada e testada apenas para queries do tipo SELECT.
    """

    def __init__(self, qres):
        self.data = qres

    def __iter__(self):
        return iter(self.data)

    def __str__(self):
        return self.data.serialize(
            encoding='latin-1', format='csv'
            ).decode('utf-8')

    def __bool__(self):
        return bool(self.data)

    def __len__(self):
        return len(self.data)

    @property
    def vars(self):
        return self.data.vars

    def save(self, fname, format='csv'):
        serialized = self.data.serialize(
            encoding='latin-1', format=format
            ).decode('utf-8')

        with open(fname, 'w') as f:
            f.write(serialized)

        return None

    def to_frame(self):
        import pandas as pd
            
        if not self.data:
            return None

        data = [
            {_recode(k): _recode(v) for k, v in item.items()}
            for item in self.data.bindings
        ]

        return pd.DataFrame(data)

class DadosSIOP:
    """Cliente que envia as queries SPARQL ao endpoint do SIOP."""

    def __init__(self):
        store = SPARQLStore('https://www1.siop.planejamento.gov.br/sparql/')
        self.graph = Graph(store=store)

    def query(self, query_string):
        """Recebe a string query como argumento."""

        return QueryResult(self.graph.query(query_string))

    def read_query(self, from_file):
        """Lê a query de um arquivo."""

        with open(from_file) as f:
            q_str = f.read()

        return self.query(q_str)

def main(argv):
    usage = f'Usage: {argv[0]} <arquivo_com_query>'

    if len(argv) != 2:
        print(' Argumentos insuficientes.\n', usage)
        return 1

    if not os.path.isfile(argv[1]):
        print(f' Arquivo "{argv[1]}" não encontrado ou não é um arquivo.\n', usage)
        return 1

    dados = DadosSIOP()
    try:
        r = dados.read_query(argv[1])
    except:
        print('Houve um erro na query. Confira o código SPARQL para verificar sua validade')
        return 1

    print(r)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
