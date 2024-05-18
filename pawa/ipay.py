#!/usr/bin/python3
import sys
import json
from datetime import datetime, timedelta, timezone
import pytz
import time
import random
import environ
import socket
from lxml import etree
from .wrap import wrap, un_wrap


# read variables for .env file
ENV = environ.Env()
environ.Env.read_env(".env")

class Ipay:

    def __init__(self, meter, amount):
        self.ip = ENV.str("IPAY_IP", "")
        self.port = ENV.str("IPAY_PORT", "")
        self.meter = meter
        self.client = ENV.str("IPAY_CLIENT", "")
        self.amount = int(amount) * 100
        self.ref = random.randint(100000000000, 999999999999)
        self.today = datetime.now(pytz.timezone('Africa/Nairobi')).strftime("%Y-%m-%d %H:%M:%S %z")
        self.buffer_size = ENV.str("BUFFER_SIZE", "")

    def create(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket successfully created")
            s.connect((self.ip, self.port))
            print("Socket connected to {} on port {}".format(self.ip, self.port))
            return s
        except Exception as e:
            raise str(e)

    def normal_vend(self):
        # create the xml
        root = etree.Element('ipayMsg', client=self.client, term="00001", seqNum="1", time=str(self.today))
        elecMsg = etree.SubElement(root, 'elecMsg', ver="2.44")
        vendReq = etree.SubElement(elecMsg, 'vendReq')
        ref = etree.SubElement(vendReq, 'ref')
        ref.text = str(self.ref)
        amt = etree.SubElement(vendReq, 'amt', cur="KES")
        amt.text = str(self.amount)
        numTokens = etree.SubElement(vendReq, 'numTokens')
        numTokens.text = "1"
        meter = etree.SubElement(vendReq, 'meter')
        meter.text = self.meter
        payType = etree.SubElement(vendReq, 'payType')
        payType.text = 'cash'

        # convert to string
        params = etree.tostring(root, pretty_print=True, encoding='utf-8')
        data_frame = wrap(params)
        return data_frame

    def get_token(self):
        # create the socket
        s = self.create()
        s.send(self.normal_vend())
        print("Request sent : %s" % time.ctime())
        resp = s.recv(self.buffer_size)
        print("Response received : %s" % time.ctime())
        data = un_wrap(resp)
        root = etree.fromstring(data)
        my_dict = {}
        for element in root.iter():
            if element.tag == 'ipayMsg':
                my_dict['vend_time'] = element.get('time')
            if element.tag == 'res':
                my_dict['code'] = element.get('code')
            if element.tag == 'ref':
                my_dict['reference'] = element.text
            if element.tag == 'util':
                my_dict['address'] = element.get('addr')
            if element.tag == 'stdToken':
                my_dict['token'] = element.text
                my_dict['units'] = element.get('units')
                my_dict['units_type'] = element.get('unitsType')
                my_dict['amount'] = element.get('amt')
                my_dict['tax'] = element.get('tax')
                my_dict['tarrif'] = element.get('tariff')
                my_dict['description'] = element.get('desc')
                my_dict['rct_num'] = element.get('rctNum')
            data = my_dict
        print(data)
        s.close()
        return data


# buy_token = Ipay('01450344831', 50)
# buy_token.get_token()
