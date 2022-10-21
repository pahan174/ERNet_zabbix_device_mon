
from flask import Flask
from markupsafe import escape
from flask import request
from datetime import datetime
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixAPI
import json
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import sys
from pyzabbix.api import ZabbixAPIException

load_dotenv()

URL_ZABBIX = os.getenv("URL_ZABBIX", default='127.0.0.1')
USER_ZABBIX = os.getenv("USER_ZABBIX", default='Admin')
USER_PASS = os.getenv("USER_PASS", default='Admin')
GROUPID = os.getenv("GROUPID", default='1')
TEMPALTEID = os.getenv("TEMPALTEID", default='1')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('create_iot_device.log',
                              maxBytes=50000000,
                              backupCount=5, encoding='utf-8'
                              )
logger.addHandler(handler)

formatter = logging.Formatter(
    u'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.info('Скрипт запустился')
try:
    zapi = ZabbixAPI(url=URL_ZABBIX, user=USER_ZABBIX, password=USER_PASS)
    answ = zapi.api_version()
except ZabbixAPIException as e:
    logger.critical(f'Нет связи с сервером Zabbix {e}')
    sys.exit()
else:
    logger.info("Установлена связь с Zabbix API Version %s" % zapi.api_version())

app = Flask(__name__)


def zbx_data_sender(json_data, zapi):
    deveui = json_data.get('DevEUI_uplink')['DevEUI']
    packet = [
        ZabbixMetric(deveui, 'testkey', json.dumps(json_data)),
    ]
    sender = ZabbixSender(zabbix_server='10.147.150.108')
    result_send = sender.send(packet)
    if result_send.failed > 0 and result_send.failed == result_send.total:
        org_id = json_data.get('DevEUI_uplink')['CustomerID']
        try:
            api_zabbix_create_host(zapi, deveui, org_id)
        except Exception as e:
            logger.error(f'Не удалось создать устройство в Zabbix. Ошибка {e}')


def api_zabbix_create_host(zapi, deveui, id_org):
    now = datetime.now()
    desc = f'Датчик добавлен в Zabbix {now.strftime("%d-%m-%Y %H:%M")} мск.'
    answer = zapi.do_request('host.create',
                        {
                        'host': deveui,
                        'name': deveui,
                        'interfaces': {
                                'type': '1',
                                'main': '1',
                                'useip': '1',
                                'ip': '127.0.0.1',
                                'dns': '',
                                'port': '10050'
                            },
                        'groups': {'groupid': GROUPID},
                        'templates': {'templateid': TEMPALTEID},
                        'description': desc,
                        'tags': {'tag': 'Organization ID', 'value': id_org}
                    })
    hostid = answer["result"].get("hostids")
    if hostid:
        logger.info(f'Создали устройство {deveui} c id {hostid}')
    else:
        logger.error(f'Устройство не создалось. Ошибка: {answer["result"]}')


# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


# @app.route("/<name>")
# def hello(name):
#     return f"Hello, {escape(name)}!"


@app.route('/method', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.get_json().get('DevEUI_uplink'):
            zbx_data_sender(request.get_json(), zapi)
        return 'OK'
    else:
        # answer = zapi.do_request('host.create',
        #             {
        #             'host': deveui,
        #             'name': deveui,
        #             'interfaces': {
        #                     'type': '1',
        #                     'main': '1',
        #                     'useip': '1',
        #                     'ip': '127.0.0.1',
        #                     'dns': '',
        #                     'port': '10050'
        #                 },
        #             'groups': {'groupid': GROUPID},
        #             'templates': {'templateid': TEMPALTEID},
        #             'description': desc,
        #             'tags': {'tag': 'Organization ID', 'value': id_org}
        #         })
        print('Проверка')
        return "Это метод GET"
