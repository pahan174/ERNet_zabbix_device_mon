
from flask import Flask
from markupsafe import escape
from flask import request
from datetime import datetime
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixAPI
import json
import os
from dotenv import load_dotenv

load_dotenv()

# URL_API = 'http://ernet.ertelecom.ru/api/monitoring/gateways'
# TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiMzcwOTE2OWQtMDVjNS00YzBkLWJkOGUtOTNmMjg5MzVkY2I0IiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTYyMTMxNDM5OCwic3ViIjoiYXBpX2tleSJ9.utt_7dVw_mvMWI_HwLGwkwPHXNCFh6pAciwGrl64o_M'
URL_ZABBIX = os.getenv("URL_ZABBIX", default='127.0.0.1')
USER_ZABBIX = os.getenv("USER_ZABBIX", default='Admin')
USER_PASS = os.getenv("USER_PASS", default='Admin')
GROUPID = os.getenv("GROUPID", default='1')
TEMPALTEID = os.getenv("TEMPALTEID", default='1')

# TEMP_JSON = {"DevEUI_uplink":{"Time":"2022-10-19T09:03:45.438+00:00","DevEUI":"6c4756c9bd557121","FPort":"2","FCntUp":"933","ADRbit":"1","MType":"2","payload_hex":"78a30802a035e12a00000000009704a035e12a0000000000970003c879e22a000000000000","mic_hex":"6b741972","Lrcid":"","LrrRSSI":"-116","LrrSNR":"0","SpFact":"12","SubBand":"","DevLrrCnt":"4","Lrrid":"4658425300003e87","LrrLAT":"57.99918","LrrLON":"55.93696","Lrrs":[{"Lrrid":"4658425300003e87","Chain":"0","LrrRSSI":"-116","LrrSNR":"0","LrrESP":"-119.01029995663981"},{"Lrrid":"4658425300003e85","Chain":"0","LrrRSSI":"-115","LrrSNR":"0","LrrESP":"-118.01029995663981"},{"Lrrid":"4658425300003e0d","Chain":"0","LrrRSSI":"-117","LrrSNR":"-10","LrrESP":"-127.41392685158225"},{"Lrrid":"4658425300003e09","Chain":"0","LrrRSSI":"-119","LrrSNR":"-12","LrrESP":"-131.26572375596103"}],"BatteryTime":"2022-10-19T09:03:46.03649Z","BatteryLevel":"96.85","CustomerID":"103","InstantPER":"","MeanPER":"","DevAddr":"697b9100"}}


app = Flask(__name__)


def zbx_data_sender(json_data):
    deveui = json_data.get('DevEUI_uplink')['DevEUI']   
    packet = [
        ZabbixMetric('e63e51162ae0db20', 'testkey', json.dumps(json_data)),
    ]
    sender = ZabbixSender(zabbix_server='10.147.150.108')
    # sender = ZabbixSender(zabbix_server='http://mon-iot.ertelecom.ru/zabbix')
    result_send = sender.send(packet)
    print(result_send)
    if result_send.failed > 0 and result_send.failed == result_send.total:
        org_id = json_data.get('DevEUI_uplink')['CustomerID']
        try:
            api_zabbix_create_host(deveui, org_id)
        except Exception as e:
            print(e)
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
        else:
            result_send = sender.send(packet)
            print(result_send)



def api_zabbix_create_host(deveui, id_org):
    global URL_ZABBIX, USER_ZABBIX, USER_PASS, GROUPID, TEMPALTEID
    zapi = ZabbixAPI(url=URL_ZABBIX, user=USER_ZABBIX, password=USER_PASS)
    now = datetime.now()
    desc = f'Датчик добавлен в Zabbix {now.strftime("%d-%m-%Y %H:%M")} мск.'
    zapi.do_request('host.create',
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
    print(f'запрос был. Результат {zapi}')


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
            zbx_data_sender(request.get_json())
        return 'OK'
    else:
        # print(TEMP_JSON)
        # zbx_data_sender(TEMP_JSON)
        return "Это метод GET"
