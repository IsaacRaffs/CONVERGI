# CONVERGI
A CONVERGI é uma plataforma web desenvolvida em Django para o monitoramento de contratos, convênios e termos institucionais. Seu MVP contará com funcionalidades como cadastro de documentos, busca rápida, alertas de vencimento, dashboard gerencial e relatórios exportáveis. A plataforma nasceu com o objetivo de facilitar e otimizar o trabalho dos servidores do setor de SEE, além de proporcionar um ambiente visual, intuitivo e de fácil utilização para os estudantes da UESPI, tornando a gestão e o acompanhamento de informações institucionais mais eficientes e acessíveis.


Passo a passso para instalação:

1º Instalar o python na versão 3.11.xx.

2º Clonar o repositório utilizando o ´git clone https://github.com/IsaacRaffs/CONVERGI.git´.

3º Entrar na pasta que fora clonada.

4º Criar um Virtual Environment (venv), para fazer isso, utilize os seguintes comandos:

    1ª) Criar: python -m venv env 
    2ª) Ativar:
        windows -> . .\env\Scripts\activate
        linux -> source ./env/Scripts/activate

5º Depoi de criar e ativar o env, devemos instalar as dependências necessarias para o funcionamento
do programa. 
Para fazer isso, devemos utilizar o comando: 
    `pip install -r requirements.txt`

Isso deverá instalar todas as dependências presentes no arquivo de requirements.txt

6º Depois disso, devemos utilizar os comandos:
    `python .\manage.py makemigrations`
    `python .\manage.py migrate`
    `python .\manage.py createsuperuser`
    `python .\manage.py runserver`

Esses comandos vão ser utilizados para configurar o servidor e inicia-lo após o último comando. 

7º Após o comando de `runserver`, será aberto um servidor local em `http://127.0.0.1:8000/`
com uma lista de empresas que está presente no arquivo do `db.sqlite`.

8º A administração do site fica localizado em `http://127.0.0.1:8000/admin/`


