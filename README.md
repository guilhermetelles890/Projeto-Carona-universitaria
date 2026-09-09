# UniDriver 

O UniDriver é um sistema de caronas universitárias desenvolvido para facilitar a oferta e a solicitação de caronas entre membros da comunidade acadêmica. O sistema busca oferecer uma alternativa mais organizada, prática e confiável aos métodos informais utilizados para combinar caronas.

## Integrantes
- Guilherme Telles dos Santos 
- Mikael Brandão 
- Matheus Fernandes

## Funcionalidades

- Cadastro de usuários;
- Login de usuários;
- Cadastro como motorista, passageiro ou ambos;
- Publicação de caronas;
- Busca de caronas disponíveis;
- Solicitação de carona;
- Aceitação ou recusa de solicitações pelo motorista;
- Controle de vagas disponíveis;
- Visualização das solicitações realizadas;
- Visualização das solicitações recebidas;
- Avaliação do motorista com nota e comentário.

## Tecnologias utilizadas

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- SQLite
- Git
- GitHub


## Banco de dados

O UniDriver utiliza o SQLite para armazenamento das informações do sistema.

O banco de dados armazena informações referentes a:

- Usuários;
- Trajetos;
- Solicitações de carona;
- Avaliações.

As tabelas são criadas automaticamente durante a inicialização do sistema.

As senhas dos usuários são armazenadas utilizando hash, evitando que sejam salvas diretamente em texto simples.

## Como executar

Para executar o UniDriver, é necessário ter o Python instalado no computador, clonar o repositório e seguir os passos abaixo:


### 1. Instalar as dependências

Execute:

    pip install -r requirements.txt

### 2. Executar o sistema

O projeto deve ser iniciado pelo arquivo `run.py`.

Execute:

    python run.py

Após executar o comando, o Flask iniciará o servidor local.

### 3. Acessar o sistema

Abra o navegador e acesse:

    http://127.0.0.1:5000
