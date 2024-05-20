# dadossiop

dadossiop é um módulo simples para facilitar consultas ao endpoint SPARQL do SIOP,
Sistema de Integrado de Planejamento e Orçamento, vinculado à Secretaria de
Orçamento do Ministério do Planejamento.

Para isso, ele expõe a classe DadosSIOP(), que se conecta ao
endpoint do SIOP e envia as queries no formato SPARQL.

O módulo pode ser utilizado em algum código python:
```
from dadossiop import DadosSIOP
dados = DadosSIOP()
r = dados.query(query_string)
```

Ou, como um script standalone:
```
python dadossiop.py <arquivo_contendo_a_query>
```

No segundo caso, o output será escrito em stdout, serializado como um CSV,
e pode ser direcionado a um arquivo usando lógica padrão de direcionamento no terminal.
Ex.
```
python dadossiop.py arquivo_contendo_a_query > output.csv
```


A documentação sobre o SIOP pode ser encontrada em
https://orcamento.dados.gov.br

Para utilizar, basta copiar o módulo e o certificado do SIOP para a pasta do seu projeto.

## Dependências
- [rdflib](https://github.com/RDFLib/rdflib)
- [pandas](https://github.com/pandas-dev/pandas) (opcional)
