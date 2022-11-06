#!/usr/bin/python
import sys
import usb.core
# find USB devices
dev = usb.core.find(find_all=True)


for cfg in dev:
    #cfg.set_configuration()
    print(cfg.product)
    # langid = 0x????
    # foo = cfg.serial_number
    # foo = usb.util.get_string(cfg, cfg.iSerialNumber)
    # print(foo)
    #     print(cfg.manufacturer)
    # print(str(cfg.idVendor), str(cfg.idProduct), cfg.backend, cfg.iSerialNumber)
    # sys.stdout.read('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + ' ,' + str(cfg.product) + '\n')
    # sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

# busses = usb.busses()
# for bus in busses:
#     devices = bus.devices
#     # print(devices)
#     for dev in devices:
#         print(dev.iProduct, dev.iSerialNumber, dev.iManufacturer, dev.filename)


# import re
# import subprocess
# device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
# # df = subprocess.check_output("lsusb")
# df = subprocess.check_output("ls /dev")
# devices = []
# print(df)
# for i in df.splitlines():
#     print(i)
    # print(i)
    # if i:
    #     info = device_re.match(i)
    #     if info:
    #         dinfo = info.groupdict()
    #         dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
    #         devices.append(dinfo)
# print(devices)
#

# import os
#
# dir = os.listdir('/dev/')
#
# for i in dir:
#     if i.startswith('ttyUSB'):
#         print(i)