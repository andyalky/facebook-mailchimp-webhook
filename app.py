from flask import Flask, request

from facebookads.adobjects.lead import Lead
from facebookads.api import FacebookAdsApi
import mailchimp

import os
import json

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = os.environ.get('MAILCHIMP_LIST_ID')

app = Flask(__name__)

def processLead(lead_data):

    subscriber_info = {}

    for fields in lead_data['field_data']:
        subscriber_info[fields['name']] = fields['values'][0]

    mailchimp_api = mailchimp.Mailchimp(MAILCHIMP_API_KEY)
    mailchimp_api.lists.subscribe(MAILCHIMP_LIST_ID, subscriber_info)

@app.route('/')
def index():
    return "Hello"

@app.route('/webhook/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        #https://developers.facebook.com/docs/graph-api/webhooks#setupget
        if request.args.get('hub.verify_token') == FB_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        else:
            return "Token Verification Failed"
    else:
        FacebookAdsApi.init(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_ACCESS_TOKEN)

        leadgen_info = json.loads(request.data)
        lead_id = leadgen_info['entry'][0]['changes'][0]['value']['leadgen_id']
        lead = Lead(lead_id)
        lead_data = lead.remote_read()

        processLead(lead_data)

        return "Success"
