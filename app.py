from asyncio import constants
import os

import openai
import jwt
import requests
import json
from time import time
from flask import Flask, redirect, render_template, request, url_for, jsonify
# from flask_cors import CORS, cross_origin

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from constants import ASSEMBO_CONTACT, sendgrid_templates

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

API_KEY='1xEu6h9GT6Sbd8CMUl7qCg'

API_SEC='SSnUyuGMw9RdeKDQKiwY1wzZt7EPrrvc'

REDIRECT_URI='https%3A%2F%2Fa4ae-27-58-74-4.in.ngrok.io'
meetingId=9373841624

userId='Gu851rCjRQKYLtsGWYKcvw'
def generateToken(code):
    headers={
        'Authorization': 'Basic MXhFdTZoOUdUNlNiZDhDTVVsN3FDZzpTU25VeXVHTXc5UmRlS0RRS2l3WTF3elp0N0VQcnJ2Yw==',
     }
    payload = {}
    token=requests.post(f'https://zoom.us/oauth/token?grant_type=authorization_code&code={code}&redirect_uri=https://a4ae-27-58-74-4.in.ngrok.io',headers=headers,data=payload)
    # # token = jwt.encode(
    # #     # Create a payload of the token containing API Key & expiration time
    # #     {'iss': API_KEY, 'exp': time() + 5000},
    # #     # Secret used to generate token signature
    # #     API_SEC,
    # #     # Specify the hashing alg
    # #     algorithm='HS256'
    # #     # Convert token to utf-8
    # # )
    tokenInfo=token.text.encode('utf8')
    accessToken=json.dumps(tokenInfo[0])
    print(tokenInfo)
    getLocalRecording(accessToken)
    return token
    # send a request with headers including a token

def getLocalRecording(accessToken):
    headers={'authorization': 'Bearer ' + accessToken}
    r=requests.get(f'https://api.zoom.us/v2/meetings/{meetingId}/token', headers=headers)
    print("\n Let's see what we get")
    print(r.text)


#fetching zoom meeting info now of the user, i.e, YOU
# def getUsers():
#     headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}

#     r = requests.get('https://api.zoom.us/v2/users/', headers=headers)
#     print("\n fetching zoom meeting info now of the user ... \n")
#     print(r.text)


#fetching zoom meeting participants of the live meeting

# def getMeetingParticipants():
#     headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}
#     r = requests.get(
#         f'https://api.zoom.us/v2/metrics/meetings/{meetingId}/participants', headers=headers)
#     print("\n fetching zoom meeting participants of the live meeting ... \n")

#     # you need zoom premium subscription to get this detail, also it might not work as i haven't checked yet(coz i don't have zoom premium account)

#     print(r.text)


# this is the json data that you need to fill as per your requirement to create zoom meeting, look up here for documentation
# https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingcreate


# meetingdetails = {"topic": "The title of your zoom meeting",
#                   "type": 2,
#                   "start_time": "2019-06-14T10: 21: 57",
#                   "duration": "45",
#                   "timezone": "Europe/Madrid",
#                   "agenda": "test",

#                   "recurrence": {"type": 1,
#                                  "repeat_interval": 1
#                                  },
#                   "settings": {"host_video": "true",
#                                "participant_video": "true",
#                                "join_before_host": "False",
#                                "mute_upon_entry": "False",
#                                "watermark": "true",
#                                "audio": "voip",
#                                "auto_recording": "cloud"
#                                }
#                   }

# def createMeeting():
#     headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}
#     r = requests.post(
#         f'https://api.zoom.us/v2/users/{userId}/meetings', headers=headers, data=json.dumps(meetingdetails))

#     print("\n creating zoom meeting ... \n")
#     print(r.text)

# def getRecording():
#     headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}
#     r=requests.get(f'https://api.zoom.us/v2/meetings/{meetingId}/jointoken/local_recording', headers=headers)
#     print("\n getting recording")
#     print(r.text)
# getUsers()
# # getMeetingParticipants()
# createMeeting()
# getRecording()
# cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/',methods=['GET', 'POST'])
def hello():
    code=request.args.get('code')
    token=generateToken(code)
    return "This is Assembo's zoom server"

@app.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    # Other headers can be added here if required
    return response

@app.route("/todo", methods=("GET", "POST"))
def todo():
    # if request.method == "POST" :
    # animal = request.get_json(force=True)
    animal = request.args.get('text')
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=generate_prompt(animal + '\ngenerate action items:'),
        temperature=0.6,
        max_tokens=500,
    )
    return response.choices[0].text

@app.route("/send_email", methods=("GET", "POST"))
def send_email():
    template_id = sendgrid_templates["POST_MEETING"]
    try:
        to_email = request.args.get('toEmail')
        notes = request.args.get('notes')
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY", default = None))
        data = {
            "personalizations": [{
                "to": [{
                    "email": to_email
                }],
                'dynamic_template_data': { "notes": notes }
            }],
            "from": {
                "email": ASSEMBO_CONTACT
            },
            "template_id": template_id
        }
        # response = sg.send(message)
        response = sg.client.mail.send.post(request_body=data)
        return "200"
    except Exception as e:
        print(e)
        return "sad"

def generate_prompt(animal):
    return animal