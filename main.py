import os
import time
import json
import datetime
import subprocess
from pythonping import ping
from influxdb import InfluxDBClient
from multiprocessing import Process

# InfluxDB Settings
NAMESPACE = os.environ.get('NAMESPACE', 'None')
DB_ADDRESS = os.environ.get('INFLUX_DB_ADDRESS', 'influxdb')
DB_PORT = int(os.environ.get('INFLUX_DB_PORT', '8086'))
DB_USER = os.environ.get('INFLUX_DB_USER', '')
DB_PASSWORD = os.environ.get('INFLUX_DB_PASSWORD', '')
DB_DATABASE = os.environ.get('INFLUX_DB_DATABASE', 'speedtests')
DB_TAGS = os.environ.get('INFLUX_DB_TAGS', None)
PING_TARGETS = os.environ.get('PING_TARGETS', '1.1.1.1, 8.8.8.8')

# Speedtest Settings
TEST_INTERVAL = float(os.environ.get('SPEEDTEST_INTERVAL', '5')) * 60
TEST_FAIL_INTERVAL = float(os.environ.get('SPEEDTEST_FAIL_INTERVAL', '5')) * 60
SERVER_ID = os.environ.get('SPEEDTEST_SERVER_ID', '')
PING_INTERVAL = float(os.environ.get('PING_INTERVAL', '5')) * 60

influxdb_client = InfluxDBClient(
    DB_ADDRESS, DB_PORT, DB_USER, DB_PASSWORD, None
)

def init_db():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == DB_DATABASE, databases))) == 0:
        influxdb_client.create_database(
            DB_DATABASE)
    else:
        influxdb_client.switch_database(DB_DATABASE)

def pkt_loss(data):
    if 'packetLoss' in data.keys():
        return int(data['packetLoss'])
    else:
        return 0

def tag_selection(data):
    tags = DB_TAGS
    options = {}
    tag_switch = {
        'namespace': NAMESPACE,
        'isp': data['isp'],
        'interface': data['interface']['name'],
        'internal_ip': data['interface']['internalIp'],
        'interface_mac': data['interface']['macAddr'],
        'vpn_enabled': (False if data['interface']['isVpn'] == 'false' else True),
        'external_ip': data['interface']['externalIp'],
        'server_id': data['server']['id'],
        'server_name': data['server']['name'],
        'server_location': data['server']['location'],
        'server_country': data['server']['country'],
        'server_host': data['server']['host'],
        'server_port': data['server']['port'],
        'server_ip': data['server']['ip'],
        'speedtest_id': data['result']['id'],
        'speedtest_url': data['result']['url']
    }
    if tags is None:
        tags = 'namespace'
    elif '*' in tags:
        return tag_switch
    else:
        tags = 'namespace, ' + tags
    tags = tags.split(',')
    for tag in tags:
        tag = tag.strip()
        options[tag] = tag_switch[tag]
    return options


def format_for_influx(data):
    influx_data = [
        {
            'measurement': 'ping',
            'time': data['timestamp'],
            'fields': {
                'jitter': data['ping']['jitter'],
                'latency': data['ping']['latency']
            }
        },
        {
            'measurement': 'download',
            'time': data['timestamp'],
            'fields': {
                'bandwidth': data['download']['bandwidth'] / 125000,
                'bytes': data['download']['bytes'],
                'elapsed': data['download']['elapsed']
            }
        },
        {
            'measurement': 'upload',
            'time': data['timestamp'],
            'fields': {
                'bandwidth': data['upload']['bandwidth'] / 125000,
                'bytes': data['upload']['bytes'],
                'elapsed': data['upload']['elapsed']
            }
        },
        {
            'measurement': 'packetLoss',
            'time': data['timestamp'],
            'fields': {
                'packetLoss': pkt_loss(data)
            }
        },
        {
            'measurement': 'speeds',
            'time': data['timestamp'],
            'fields': {
                'jitter': data['ping']['jitter'],
                'latency': data['ping']['latency'],
                'packetLoss': pkt_loss(data),
                'bandwidth_down': data['download']['bandwidth'] / 125000,
                'bytes_down': data['download']['bytes'],
                'elapsed_down': data['download']['elapsed'],
                'bandwidth_up': data['upload']['bandwidth'] / 125000,
                'bytes_up': data['upload']['bytes'],
                'elapsed_up': data['upload']['elapsed']
            }
        }
    ]
    tags = tag_selection(data)
    if tags is not None:
        for measurement in influx_data:
            measurement['tags'] = tags
    return influx_data

def speedtest():
    if not SERVER_ID:
        speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"], capture_output=True)
        print("Automatic server choice")
    else:
        speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json", "--server-id=" + SERVER_ID], capture_output=True)
        print("Manual server choice : ID = " + SERVER_ID)
    if speedtest.returncode == 0:
        print("Speedtest Successful :")
        data_json = json.loads(speedtest.stdout)
        print("time: " + str(data_json['timestamp']) + " - ping: " + str(data_json['ping']['latency']) + " ms - download: " + str(data_json['download']['bandwidth']/125000) + " Mb/s - upload: " + str(data_json['upload']['bandwidth'] / 125000) + " Mb/s - isp: " + data_json['isp'] + " - ext. IP: " + data_json['interface']['externalIp'] + " - server id: " + str(data_json['server']['id']) + " (" + data_json['server']['name'] + " @ " + data_json['server']['location'] + ")")
        data = format_for_influx(data_json)
        if influxdb_client.write_points(data) == True:
            print("Data written to DB successfully")
    else:
        print("Speedtest Failed :")
        print(speedtest.stderr)
        print(speedtest.stdout)

def main():
    pSpeed = Process(target=speedtest)
    init_db()
    loopcount = 0
    while (1):
        if loopcount == 0 or loopcount % PING_INTERVAL == 0:
            if pPing.is_alive():
                pPing.terminate()
            pPing = Process(target=pingtest)
            pPing.start()
        if loopcount == 0 or loopcount % TEST_INTERVAL == 0:
            if pSpeed.is_alive():
                pSpeed.terminate()
            pSpeed = Process(target=speedtest)
            pSpeed.start()
        if loopcount % ( PING_INTERVAL * TEST_INTERVAL ) == 0:
            loopcount = 0
        time.sleep(1)
        loopcount += 1
if __name__ == '__main__':
    print('Speedtest CLI data logger to InfluxDB started...')
    main()