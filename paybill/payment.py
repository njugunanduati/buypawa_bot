import requests
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth


class Payment:

    def __init__(self):
        self.consumer_key = 'GG7dWH41J62SfBZIAwR5HRFdq3BkbVxt'
        self.consumer_secret = 'd41f98AAHIy4gFGO'
        self.api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    def get_access_token(self):
        r = requests.get(self.api_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        mpesa_access_token = r.json()
        return mpesa_access_token['access_token']

    def online_payment(self, phone_number):
        access_token = str(self.get_access_token())
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        business_short_code = '174379'
        pass_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
        print("time", lipa_time)
        data_to_encode = business_short_code + pass_key + lipa_time
        online_password = base64.b64encode(data_to_encode.encode())
        decode_password = online_password.decode('utf-8')
        request = {
            "BusinessShortCode": business_short_code,
            "Password": decode_password,
            "Timestamp": lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": 1,
            "PartyA": phone_number,  # replace with your phone number to get stk push 254729556997
            "PartyB": business_short_code,
            "PhoneNumber": phone_number,  # replace with your phone number to get stk push
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "BuyPawa",
            "TransactionDesc": "Testing stk push"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return response.json()
