
from flask import Flask
from markupsafe import escape
from flask import request
from datetime import datetime
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixAPI

# URL_API = 'http://ernet.ertelecom.ru/api/monitoring/gateways'
# TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiMzcwOTE2OWQtMDVjNS00YzBkLWJkOGUtOTNmMjg5MzVkY2I0IiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTYyMTMxNDM5OCwic3ViIjoiYXBpX2tleSJ9.utt_7dVw_mvMWI_HwLGwkwPHXNCFh6pAciwGrl64o_M'
# URL_ZABBIX = 'http://10.147.150.108'
URL_ZABBIX = 'http://mon-iot.ertelecom.ru/zabbix'
USER_ZABBIX = 'Admin'
USER_PASS = 'QMD~7H%%'
GROUPID = '27'
TEMPALTEID = '11488'

TEMP_JSON = {'DevEUI_uplink': {'Time': '2022-10-19T09:03:45.438+00:00', 'DevEUI': '6c4756c9bd557191', 'FPort': '2', 'FCntUp': '931', 'ADRbit': '1', 'MType': '2', 'payload_hex': '78a30802a035e12a00000000009704a035e12a0000000000970003c879e22a000000000000', 'mic_hex': '6b741972', 'Lrcid': '', 'LrrRSSI': '-116', 'LrrSNR': '0', 'SpFact': '12', 'SubBand': '', 'DevLrrCnt': '4', 'Lrrid': '4658425300003e87', 'LrrLAT': '57.99918', 'LrrLON': '55.93696', 'Lrrs': [{'Lrrid': '4658425300003e87', 'Chain': '0', 'LrrRSSI': '-116', 'LrrSNR': '0', 'LrrESP': '-119.01029995663981'}, {'Lrrid': '4658425300003e85', 'Chain': '0', 'LrrRSSI': '-115', 'LrrSNR': '0', 'LrrESP': '-118.01029995663981'}, {'Lrrid': '4658425300003e0d', 'Chain': '0', 'LrrRSSI': '-117', 'LrrSNR': '-10', 'LrrESP': '-127.41392685158225'}, {'Lrrid': '4658425300003e09', 'Chain': '0', 'LrrRSSI': '-119', 'LrrSNR': '-12', 'LrrESP': '-131.26572375596103'}], 'BatteryTime': '2022-10-19T09:03:46.03649Z', 'BatteryLevel': '96.85', 'CustomerID': '103', 'InstantPER': '', 'MeanPER': '', 'DevAddr': '697b9100'}}


app = Flask(__name__)


def zbx_data_sender(json_data):
    print(json_data)
    DEVEUI = json_data.get('DevEUI_uplink')['DevEUI']
    packet = [
        ZabbixMetric(DEVEUI, 'testkey', json_data),
    ]
    sender = ZabbixSender(use_config=True)
    # sender = ZabbixSender(zabbix_server='http://mon-iot.ertelecom.ru/zabbix')
    result_send = sender.send(packet)
    print(result_send)
    # if result_send.failed > 0 and result_send.failed == result_send.total:
    #     try:
    #         api_zabbix_create_host(json_data['id'][-8:], json_data['name'])
    #     except Exception as e:
    #         if 'Host with the same visible name' in e.data:
    #             #print(f'У БС {json_data["name"]} сменился ID. Новый ID {json_data["id"][-8:]}')  
    #             update_id_bs(json_data["name"], json_data["id"][-8:])
    #             send_email(json_data['id'], json_data['name'])
    #         else:
    #             f = open('/usr/share/zabbix/Sender_LOG_' + datetime.now().strftime("%d-%m-%Y") + '.log', 'a', encoding='utf-8')
    #             f.write(f'{datetime.now().strftime("%d-%m-%Y")}; {datetime.now().strftime("%H:%M")} ; {json_data["id"][-8:]} ; {json_data["name"]} ; BS снята с мониторинга\n')
    #             f.close()
    #             #print(f'БС с ID {json_data["id"][-8:]} снята с мониторинга')
    #     else:
    #         send_email(json_data['id'], json_data['name'])
    #         f = open('/usr/share/zabbix/Sender_LOG_' + datetime.now().strftime("%d-%m-%Y") + '.log', 'a', encoding='utf-8')
    #         f.write(f'{datetime.now().strftime("%d-%m-%Y")}; {datetime.now().strftime("%H:%M")} ; {json_data["id"][-8:]} ; {json_data["name"]} ; На сервер добавлена новая БС\n')
    #         f.close()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"

@app.route('/method', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.get_json().get('DevEUI_uplink'):
            print(request.get_json())
        return 'OK'
    else:
        # print(TEMP_JSON)
        zbx_data_sender(TEMP_JSON)
        return "Это метод GET"
