import configparser
import glob
import time

import requests
import re

import os


# config = configparser.ConfigParser()
# config.read('config2.ini')


# api_url_base = 'http://'+config.get('dados_api', 'server')+':'+config.get('dados_api', 'port') + '/'
#
# dir_local = os.getcwd()
#
# loguin = {
#     "username": config.get('dados_api', 'uid'),
#     "password": config.get('dados_api', 'pwd'),
#     "method": "OAuth2PasswordBearer",
# }


def verifica_config(name_config):
    config = configparser.ConfigParser()
    config.read(name_config)
    user = config.get('dados_api', 'uid')
    password = config.get('dados_api', 'pwd')
    siteid = config.get('dados_api', 'siteid')

    if not siteid:
        siteid = input('Digite o site id: ')
        config.set('dados_api', 'siteid', siteid)
    if not user:
        user = input('Digite o nome de usuario: ')
        config.set('dados_api', 'uid', user)
    if not password:
        password = input('Digite a senha: ')
        config.set('dados_api', 'pwd', password)

    with open(name_config, 'w') as configfile:
        config.write(configfile)

    return config


def download_version(site, ver, dir_local, api_url_base, loguin):
    token = requests.post(api_url_base + 'token', data=loguin, verify=False)

    headers = {
        "Authorization": "Bearer %s" % token.json()['access_token']
    }
    data = {
        'siteid': site,
        'version': ver
    }

    res = requests.get(api_url_base + 'getversion', params=data, headers=headers, verify=False)

    if res.text == '{"versao":"OK"}':
        file = dir_local + '\\version\\maquina_' + version + '.py'
        print('Não há atualizações disponiveis, abrindo sistema.')
        return file
    else:
        print('Atualização disponivel, baixando arquivos')
        file = dir_local + '\\version\\maquina_' + version + '.py'
        os.remove(file)
        d = res.headers['content-disposition']
        fname = (re.findall("filename=(.+)", d)[0]).replace('"', '')
        pasta = 'version'
        print('Criando arquivo')
        open(dir_local + '\\' + pasta + '\\' + fname, "wb").write(res.content)
        file = dir_local + '\\' + pasta + '\\' + fname
        print('Atualização efetuada com sucesso.')

        return file


def get_version(dir_local):
    for i in glob.glob(dir_local + '\\version\\maquina_*'):
        versao = i.replace('.py', '')
        versao = str(versao.split('\\')[-1]).replace('maquina_', '')

        return versao


while True:
    # siteid = 'DEFAULT'
    # print('Buscando atualizações')
    config = verifica_config('config.ini')  # config =
    user = config.get('dados_api', 'uid')
    password = config.get('dados_api', 'pwd')
    siteid = config.get('dados_api', 'siteid')


    api_url_base = 'https://'+config.get('dados_api', 'server')+':'+config.get('dados_api', 'port') + '/'
    print(api_url_base)

    dir_local = os.getcwd()

    loguin = {
        "username": config.get('dados_api', 'uid'),
        "password": config.get('dados_api', 'pwd'),
        "method": "OAuth2PasswordBearer",
    }

    print(siteid, password, user)

    version = get_version(dir_local)
    print(version)
    arquivo = download_version(siteid, version, dir_local, api_url_base, loguin)
    print(arquivo)
    print('Abrindo sistema.')
    # time.sleep(10)
    exec(open(arquivo).read())



