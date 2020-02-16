# Sigaa-api

API não oficial do sistema integrado de gestão e atividades da Universidade Federal do Piauí. Este projeto não possui nenhum tipo de ligação com a UFPI e o STI.

## Instalação

Para instalar basta criar um ambiente virtual com o _software_ de sua preferência, ex:

```sh
$ virtualenv sigaa-api
```

Entrar no ambiente virtual recem criado, clonar o repositório utilizando o comando:

```sh
$ git clone https://github.com/sosolidkk/sigaa-api.git
```

Após o término, basta ativar o ambiente rodando `$ source bin/activate`. Com o ambiente virtual ativado, entre na pasta e instale as dependências do projeto com o comando `pip install -r requirements.txt`.

Após finalizar a instalação das dependências, para rodar digite o comando `$ uvicorn main:app`.

## Utilizando

Atualmente só possui duas funcionalidades, que são retornar as informações do usuário e seu histórico de notas. Para ver com mais detalhes, basta acessar a url inicial da [API](http://127.0.0.1:8000/docs) após rodar o comando do `uvicorn`. Nessa página, você vai ter um ambiente totalmente interativo para poder testar direto do seu navegador as requisições nas rotas existentes.

## Contribuindo

Para contribuir basta realizar aquele fork maroto, adicionar umas coisas ou editar e gerar aquela(s) PR(s) no final de tudo.

## Créditos

- [Sosolidkk](https://github.com/sosolidkk)
- [Mex978](https://github.com/Mex978)

## To Do

* [X] Adicionar opção para retornar as turmas do aluno

* [ ] Adicionar a opção de buscar dados de uma turma pelo ID da mesma

* [ ] Adicionar a opção de retornar o calendário acadêmico do período atual

* [ ] Adicionar a opção de retornar o atestado de matrícula

* [ ] Adicionar a opção de retornar o histórico do aluno
