import configparser
import glob

import requests
import re

import os


config = configparser.ConfigParser()
config.read('config.ini')


api_url_base = 'https://'+config.get('dados_api', 'server')+':'+config.get('dados_api', 'port') + '/'

dir_local = os.getcwd()

loguin = {
    "username": config.get('dados_api', 'uid'),
    "password": config.get('dados_api', 'pwd'),
    "method": "OAuth2PasswordBearer",
}


def download_version(site, ver):
    print(api_url_base + 'token')
    token = requests.post(api_url_base + 'token', data=loguin, verify=False)

    headers = {
        "Authorization": "Bearer %s" % token.json()['access_token']
    }
    data = {
        'siteid': site,
        'version': ver
    }

    res = requests.get(api_url_base + 'getversion', params=data, headers=headers, verify=False)
    print(res.reason)
    if res.text == '{"versao":"OK"}':
        file = dir_local + '/version/maquina_' + version + '.py'
        print('Não há atualizações disponiveis, abrindo sistema.')
        return file
    else:
        print('Atualização disponivel, baixando arquivos')
        file = dir_local + '/version/maquina_' + version + '.py'
        os.remove(file)
        d = res.headers['content-disposition']
        fname = (re.findall("filename=(.+)", d)[0]).replace('"', '')
        pasta = 'version'
        print('Criando arquivo')
        open(dir_local + '/' + pasta + '/' + fname, "wb").write(res.content)
        file = dir_local + '/' + pasta + '/' + fname
        print('Atualização efetuada com sucesso.')

        return file


def get_version():
    for i in glob.glob(dir_local + '/version//maquina_*'):
        print(i)
        versao = i.replace('.py', '')
        versao = str(versao.split('/')[-1]).replace('maquina_', '')

        return versao


# while True:
siteid = 'DEFAULT'
print('Buscando atualizações')
version = get_version()
print(version)
arquivo = download_version(siteid, version)
print('Abrindo sistema.')
exec(open(arquivo).read())



