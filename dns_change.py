import os
import sys
import json
import requests
import dns.resolver
import time
from collections import OrderedDict

try:
    CLIENT_ID = os.environ['ACME_CLIENT_ID']
except KeyError:
    CLIENT_ID = 970626

try:
    DOMAIN = os.environ['ACME_DOMAIN']
except KeyError:
    DOMAIN = 'jcole.nz'


def get_api_key():
    # API KEY 
    return ""


def add_record(record, type, content):
    uri = 'https://api.sitehost.nz/1.1/dns/add_record.json'
    body = OrderedDict()
    body['apikey'] = get_api_key()
    body['client_id'] = CLIENT_ID
    body['domain'] = DOMAIN
    body['type'] = type
    body['name'] = record
    body['content'] = content
    return requests.post(uri, data=body).json()


def list_records():
    return requests.get(f'https://api.sitehost.nz/1.1/dns/list_records.json?apikey={get_api_key()}&client_id={CLIENT_ID}&domain={DOMAIN}').json()


def del_record(record_id):
    uri = 'https://api.sitehost.nz/1.1/dns/delete_record.json'
    body = OrderedDict()
    body['apikey'] = get_api_key()
    body['client_id'] = CLIENT_ID
    body['domain'] = DOMAIN
    body['record_id'] = record_id
    return requests.post(uri, data=body).json()


def check_for_txt_record(record, contents):
    try:
        answers = dns.resolver.resolve(record, 'TXT')
        for rdata in answers:
            for txt_string in rdata.strings:
                if contents in str(txt_string):
                    return True
            else:
                return False
    except dns.resolver.NoAnswer:
        return False


if __name__ == "__main__":
    if sys.argv[1] == 'create':

        if (msg := add_record('_acme-challenge.' + os.environ['CERTBOT_DOMAIN'], 'TXT', os.environ['CERTBOT_VALIDATION'])['msg']) != "Successful.":

            print(
                f"Failed adding record {os.environ['CERTBOT_DOMAIN']},{os.environ['CERTBOT_VALIDATION']}: {msg}")

        while check_for_txt_record('_acme-challenge.' + os.environ['CERTBOT_DOMAIN'], os.environ['CERTBOT_VALIDATION']) is not True:
            print("Not yet resolved")
            time.sleep(15)

    elif sys.argv[1] == 'del':

        del_records = [r['id'] for r in list_records()['return'] if
                    r['name'] == '_acme-challenge.' + os.environ['CERTBOT_DOMAIN'] and
                    r['content'] == os.environ['CERTBOT_VALIDATION'] and
                    r['type'] == 'TXT']

        for record_id in del_records:

            if (msg := del_record(record_id)['msg']) != "Successful.":

                print(
                    f"Failed deleting record {record_id},{os.environ['CERTBOT_DOMAIN']},{os.environ['CERTBOT_VALIDATION']}: {msg}")
