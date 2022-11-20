import configparser
import glob
import time

import requests
import re

import os

import logging


dir_local = '/home/pedro/BiometriaProject/maquina/'

logging.basicConfig(filename= dir_local + '/logs/executor.log', level=logging.DEBUG, filemode='a+',
                    format='%(asctime)s - %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')


# logging.info('')
# logging.error('')
# logging.warning('')



def verifica_config(name_config):
    '''Esse modulo verifica se o config file esta com todos os dados necessarios presentes.'''
    try:
        logging.info('Tentando encontrar o arquivo de config.')
        config = configparser.ConfigParser()
        config.read(name_config)
        logging.info('Config encontrado.')
        user = config.get('dados_api', 'uid')
        password = config.get('dados_api', 'pwd')
        siteid = config.get('dados_api', 'siteid')
        if not siteid or not user or not password:
            if not siteid:
                logging.info('Siteid ausente. - solicitando ao usuario')
                siteid = input('Digite o site id: ')
                config.set('dados_api', 'siteid', siteid)
            if not user:
                logging.info('Nome de usuario ausente. - solicitando ao usuario')
                user = input('Digite o nome de usuario: ')
                config.set('dados_api', 'uid', user)
            if not password:
                logging.info('Senha nao encontrada - solicitando ao usuario')
                password = input('Digite a senha: ')
                config.set('dados_api', 'pwd', password)

        with open(name_config, 'w') as configfile:
            config.write(configfile)

        return config
    except OSError as e:
        logging.error(e)
        pass


def download_version(site, ver, dir_local, api_url_base, loguin):
        def conect_version():
            '''Essa funcao faz a conexao com a api para obter a versao.'''
            try:
                logging.info('Buscando token de API')
                token = requests.post(api_url_base + 'token', data=loguin, verify=False)
                if token:
                    logging.info('Token encontrado com sucesso.')
                    headers = {
                        "Authorization": "Bearer %s" % token.json()['access_token']
                    }

                    data = {
                        'siteid': site,
                        'version': ver
                    }
                    logging.info('Buscando versao na api.')
                    res = requests.get(api_url_base + 'getversion', params=data, headers=headers, verify=False)
                    if res:
                        logging.info(f'Versao encontrada.')
                        return res
                    else:
                        logging.warning('Nao foi possivel se conectar a API para buscar a versao.')

            except OSError as oe:
                logging.error(oe)
                pass
            except requests.exceptions.Timeout as to:
                logging.error(to)

            except requests.exceptions.TooManyRedirects as tm:
                logging.error(tm)

            except requests.exceptions.HTTPError as he:
                logging.error(he)

            except requests.exceptions.ConnectionError as ce:
                logging.error(ce)


        res = conect_version()

        if res:
            logging.info('Comparando versoes.')
            if res.text == '{"versao":"OK"}':
                file = dir_local + 'version/maquina_' + version + '.py'
                print('Não há atualizações disponiveis, abrindo sistema.')
                logging.info('Não há atualizações disponiveis, abrindo sistema.')
                return file
            else:
                print('Atualização disponivel, baixando arquivos')
                logging.info('Atualização disponivel, baixando arquivos')


                old_file = dir_local + 'version/maquina_' + version + '.py'
                if old_file:
                    logging.info('Deletando versao antiga.')
                    os.remove(old_file)
                else:
                    logging.warning('Nao foi encontrado arquivo antigo.')

                d = res.headers['content-disposition']
                fname = (re.findall("filename=(.+)", d)[0]).replace('"', '')
                pasta = 'version'

                if d and fname and pasta:
                    logging.info('Criando arquivo.')
                    print('Criando arquivo')

                    open(dir_local + pasta + '/' + fname, "wb").write(res.content)
                    file = dir_local + pasta + '/' + fname

                    print('Atualização efetuada com sucesso.')
                    logging.info('Atualização efetuada com sucesso.')

                    return file
                else:
                    logging.warning('Nao foi possivel baixar o arquivo de atualizacao.')

def get_version(dir_local):

    try:
        if dir_local:
            for i in glob.glob(dir_local + 'version/maquina_*'):
                versao = i.replace('.py', '')
                versao = str(versao.split('/')[-1]).replace('maquina_', '')
                if versao:
                    logging.info(f'Versao encontrada -- {versao}.')
                    return versao
                else:
                    logging.warning('Versao nao encontrada.')
                    pass
    except OSError as e:
        logging.error(e)


# while True:
    # siteid = 'DEFAULT'
    # print('Buscando atualizações')
# dir_local = os.getcwd()

print(dir_local + 'config.ini')
'''Verificando config file'''

# Buscando dados de login
try:
    logging.info('Buscando arquivo de configuracao.')
    config = verifica_config(dir_local + 'config.ini')
    user = config.get('dados_api', 'uid')
    password = config.get('dados_api', 'pwd')
    siteid = config.get('dados_api', 'siteid')
    if user and password and siteid:
        logging.info('Dados de configuração -- ok')
        loguin = {
            "username": config.get('dados_api', 'uid'),
            "password": config.get('dados_api', 'pwd'),
            "method": "OAuth2PasswordBearer",
        }
    else:
        loguin = None
        logging.warning('Arquivo de configuracao incompleto.')
except OSError as e:
    logging.error(e)


# buscando dados de servidor.
try:
    logging.info('Buscando dados de conexao no arquivo de configuracao')
    server = config.get('dados_api', 'server')
    port = config.get('dados_api', 'port')
    if server and port:
        api_url_base = 'https://' + server + ':' + port + '/'
    else:
        api_url_base = None
        logging.warning('Informações do servidor não disponiveis no config.')
except OSError as e:
    logging.error(e)


try:
    while True:
        logging.info('Buscando versao atual')
        print('Buscando versao atual')
        version = get_version(dir_local)
        if version:
            logging.info('Verificando versao disponivel.')
            print('Verificando versão disponivel.')
            if siteid and version and dir_local and api_url_base and loguin:
                arquivo = download_version(siteid, version, dir_local, api_url_base, loguin)
                if arquivo:
                    print(arquivo)
                    print('Abrindo sistema.')
                    logging.info(f'Abrindo sistema -- {arquivo}')
                    exec(open(arquivo).read())
                else:
                    logging.warning('Nao foi possivel realizar a verificacao de versao -- variaveis ausentes.')
                    logging.warning('Tentando abrir arquivo padrão.')
                    arquivo_padrao = dir_local + 'version/maquina_' + version + '.py'
                    print(arquivo_padrao)
                    exec(open(arquivo_padrao).read())


            else:
                logging.warning('Nao foi possivel realizar a verificacao de versao -- variaveis ausentes.')
                logging.warning('Tentando abrir arquivo padrão.')
                arquivo_padrao = dir_local + 'version/maquina_' + version + '.py'
                print(arquivo_padrao)
                exec(open(arquivo_padrao).read())




except OSError as e:
    logging.error(e)



