from flask import Flask, request
from flask_cors import CORS

import dbHandler
import MyJWT

API_KEY = '5vtb{$&(@WI%^tvbU6*TY&%VTBt7^B&Ivt7i5tbv&;`W/o0)'
jwt = MyJWT.JWT()
jwt.JWT_DATA['SECRET_KEY'] = 'v4t13G*N-HJQ5v+173Y5+.vEbpV^BGGH60[R<8Ev63V*D+5Aa4eQ5tva]}'


app = Flask(__name__)
CORS(app)


@app.route('/login', methods=['POST'])
def login():
  if request.method == 'POST':
    username = request.json['username']
    password = request.json['password']
    uid = dbHandler.logInUser(username, password)
    if uid == -1: return {'status': 403}
    token, userContext = jwt.jwtencode({'uid': uid, 'username': username})
    return {'status': 200, 'JWT_Token': token, 'JWT_User_Context': userContext}
  return{'status': 403}


@app.route('/checkUsername')
def checkUsername():
  username = request.json['username']
  found = dbHandler.checkIfUsernameExists(username)
  return {'status': 200, 'found': found}


@app.route('/createAccount', methods=['POST'])
def createAccount():
  if request.method == 'POST' and request.json['API_KEY'] == API_KEY:
    username = request.json['username']
    password = request.json['password']
    dbHandler.addUser(username, password)
    return {'status': 200}
  return{'status': 403}


def main():
  app.run(port=5000)


if __name__ == '__main__':
  main()
