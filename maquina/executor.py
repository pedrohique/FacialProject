import configparser
import glob
import time

import requests
import re

import logging

from wifi import *
import subprocess
import os


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
        if not ver:
            ver = '1.0'
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
                if version:
                    print(dir_local , 'version/maquina_' , version , '.py')
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



# print(dir_local + 'config.ini')
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

def login_wifi():
    returned_value = subprocess.check_output('ip a | grep -i BROADCAST | cut -d: -f 2 ', shell=True)
    returned = returned_value.decode("utf-8").split('\n')
    dict_redes = {}
    tipo_certo = None

    def CreateWifiConfig(SSID, password):  # raspiberry
        # setting up file contents
        config_lines = [
            'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
            'update_config=1',
            'country=US',
            '\n',
            'network={',
            '\tssid="{}"'.format(SSID),
            '\tpsk="{}"'.format(password),
            '}'
        ]
        config = '\n'.join(config_lines)

        # display additions
        # print(config)

        # give access and writing. may have to do this manually beforehand
        # os.system('sudo chmod a+rw /etc/wpa_supplicant/wpa_supplicant.conf')
        os.system('sudo chmod a+rw teste.conf')

        # writing to file
        # with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        with open("teste.conf", "w") as wifi:
            wifi.write(config)

        # displaying success
        print("wifi config added")




    #print(tipo_certo, dict_redes[int(escolha)]['nome_rede'], cell, senha)

    for i in returned:
        tipo = i.replace(' ', '')
        try:
            cells = Cell.all(tipo)
            for id, cell in enumerate(cells):
                dict_redes[id] = {'nome_rede': cell.ssid, 'potencia': cell.signal}
            tipo_certo = tipo
        except Exception as e:
            logging.warning(e)

    if dict_redes and tipo_certo:
        print('Selecione o numero da rede: ')
        for i in dict_redes:
            print(i, ' - ', dict_redes[i]['nome_rede'], ' - Potencia: ', (100 + dict_redes[i]['potencia']))

        logging.info('Redes encontradas, solicitando login ao usuario.')

        escolha = int(input('Digite o numero da rede: '))
        senha = input('Digite sua senha: ')
        rede_escolhida = dict_redes[int(escolha)]['nome_rede']
        cells = Cell.all(tipo_certo)
        for i in cells:
            if i.ssid == rede_escolhida:
                logging.info('Rede encontrada criando arquivo de configuração.')
                CreateWifiConfig(rede_escolhida, senha)
                logging.info('Arquivo encontrado, reiniciando o sistema.')
                print('Rede configurada com sucesso. Reiniciando o sistema.')
                time.sleep(3)
                os.popen("sudo reboot")
    else:
        logging.error('Nenhuma rede encontrada, reiniciando o sistema.')
        print('Não foi encontrada nenhuma rede wifi. Reiniciando o sistema em alguns segundos.')
        time.sleep(3)





try:
    while True:
        logging.info('Buscando versao atual')
        print('Buscando versao atual')
        version = get_version(dir_local)
        if version:
            logging.info('Verificando atualizações disponiveis.')
            print('Verificando atualizações disponiveis.')
            if siteid and version and dir_local and api_url_base and loguin:
                arquivo = download_version(siteid, version, dir_local, api_url_base, loguin)
                if arquivo:
                    print('Abrindo sistema.')
                    logging.info(f'Abrindo sistema -- {arquivo}')
                    exec(open(arquivo).read())
                else:
                    logging.warning('Nao foi possivel realizar a verificacao de atualização '
                                    '-- Sem conexão com a internet.')
                    print('Nao foi possivel realizar a verificacao de atualização -- Sem conexão com a internet.')
                    resp = input('Deseja se conextar a uma rede WIFI?\n'
                                 '[1] - SIM\n'
                                 '[2] - NÃO\n')

                    if resp == '1':
                        login_wifi()

                    else:
                        logging.warning('Tentando abrir arquivo padrão.')
                        arquivo_padrao = dir_local + 'version/maquina_' + version + '.py'
                        exec(open(arquivo_padrao).read())


            else:
                logging.warning('Nao foi possivel realizar a verificacao de versao -- variaveis ausentes.')
                print('Nao foi possivel realizar a verificacao de versao -- variaveis ausentes.')
                logging.warning('Tentando abrir arquivo padrão.')
                arquivo_padrao = dir_local + 'version/maquina_' + version + '.py'
                exec(open(arquivo_padrao).read())
        else:
            logging.warning('Arquivo executor não encontrado, tentando conexão com a internet.')
            print('Seu sistema esta corrompido, tentando download da versão correta.')
            if siteid and dir_local and api_url_base and loguin:
                arquivo = download_version(siteid, version, dir_local, api_url_base, loguin)
                if arquivo:
                    print('Abrindo sistema.')
                    logging.info(f'Abrindo sistema -- {arquivo}')
                    exec(open(arquivo).read())
                else:
                    logging.warning('Não foi possivel realizar a conexão com o servidor.')
                    print('Não foi possivel realizar a conexão com o servidor.')
                    resp = input('Deseja se conextar a uma rede WIFI?\n'
                                 '[1] - SIM\n'
                                 '[2] - NÃO\n')
                    if resp == '1':
                        logging.info('Tentando conexão WIFI.')
                        login_wifi()

                    else:
                        print('Não foi possivel atualizar seu sistema, tentando execução novamente.')
                        time.sleep(3)
                        pass




except OSError as e:
    logging.error(e)



