import requests
import environ
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth

# read variables for .env file
ENV = environ.Env()
environ.Env.read_env(".env")


class Payment:

    def __init__(self):
        self.consumer_key = ENV.str("CONSUMER_KEY", "")
        self.consumer_secret = ENV.str("CONSUMER_SECRET", "")
        self.api_auth_url = ENV.str("API_AUTH_URL", "")
        self.api_url = ENV.str("API_URL", "")
        self.pass_key = ENV.str("PASS_KEY", "")
        self.business_short_code = ENV.str("BUSINESS_SHORT_CODE", "")

    def get_access_token(self):
        r = requests.get(self.api_auth_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        mpesa_access_token = r.json()
        return mpesa_access_token['access_token']

    def online_payment(self, phone_number, amount):
        access_token = str(self.get_access_token())
        api_url = ENV.str("API_URL", "")+"stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        business_short_code = self.business_short_code
        pass_key = self.pass_key
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
            "Amount": amount,
            "PartyA": phone_number,  # replace with your phone number to get stk push
            "PartyB": business_short_code,
            "PhoneNumber": phone_number,  # replace with your phone number to get stk push
            "CallBackURL": ENV.str("API_URL", ""),
            "AccountReference": ENV.str("ACCOUNT_REFERENCE", ""),
            "TransactionDesc": ENV.str("TRANSACTION_DESC", ""),
        }
        response = requests.post(api_url, json=request, headers=headers)
        return response.json()
