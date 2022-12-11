# import subprocess
#
# returned_value = subprocess.check_output('nmcli dev wifi', shell=True)
# returned = returned_value.decode("utf-8")
# #print(returned, type(returned))
# for i in returned.split('\n'):
#     print(i.split(' '))
#     print('---------------------------------------------')

from wifi import *
import subprocess
import os



returned_value = subprocess.check_output('ip a | grep -i BROADCAST | cut -d: -f 2 ', shell=True)
returned = returned_value.decode("utf-8").split('\n')
dict_redes = {}
tipo_certo = ''


def CreateWifiConfig(SSID, password):  #raspiberry
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
    os.popen("sudo chmod a+rw /etc/wpa_supplicant/wpa_supplicant.conf")
    # os.popen("sudo chmod a+rw teste.conf")

    # writing to file
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
    # with open("teste.conf", "w") as wifi:
        wifi.write(config)

    # displaying success
    print("wifi config added")

for i in returned:
    tipo = i.replace(' ', '')
    try:
        cells = Cell.all(tipo)
        for id, cell in enumerate(cells):
            dict_redes[id]={'nome_rede': cell.ssid, 'potencia': cell.signal}
        tipo_certo = i.replace(' ', '')
    except Exception as e:
        print(tipo, 'error')
print('Selecione o numero da rede: ')

for i in dict_redes:

    print(i, ' - ', dict_redes[i]['nome_rede'], ' - Potencia: ', (100 + dict_redes[i]['potencia']))


escolha = int(input('Digite o numero da rede: '))
senha = input('Digite sua senha: ')
cell = Cell.all(tipo_certo)
# print(tipo_certo, dict_redes[int(escolha)]['nome_rede'], cell, senha)
rede_escolhida = dict_redes[int(escolha)]['nome_rede']
for i in cell:
    if i.ssid == rede_escolhida:
        CreateWifiConfig(rede_escolhida, senha)
        print('Rede configurada com sucesso. Reiniciando o sistema.')
        os.popen("sudo reboot")

