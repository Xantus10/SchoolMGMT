from datetime import datetime, timedelta
from flask import Flask, request, make_response
from flask_cors import CORS

import dbHandler
from MyJWT import JWT


COOKIEEXPIRYSECONDS = 24 * 3600 # 1 day
jwt = JWT()
jwt.set_secret_key('v4t13G*N-HJQ5v+173Y5+.vEbpV^BGGH60[R<8Ev63V*D+5Aa4eQ5tva]}')
jwt.set_expires(COOKIEEXPIRYSECONDS)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173'], supports_credentials=True)


@app.route('/login', methods=['POST'])
def flask_login():
  if request.method == 'POST':
    # Get data
    username = request.json['username']
    password = request.json['password']
    # Call to DB
    uid, role = dbHandler.logInUser(username, password)
    # If login unsuccessful
    if uid == -1: return {'status': 403}
    # Make response
    resp = make_response({'status': 200})
    # Data for JWT token
    data = {'uid': uid, 'username': username, 'role': role}
    JWT_token, JWT_user_context = jwt.jwtencode(data)
    expires = datetime.now() + timedelta(seconds=COOKIEEXPIRYSECONDS)
    # Set cookies
    resp.set_cookie('JWT_token', JWT_token, expires=expires, domain='localhost')
    resp.set_cookie('JWT_user_context', JWT_user_context, httponly=True, samesite='Strict', expires=expires)
    return resp
  return{'status': 403}


@app.route('/checkUsername')
def flask_checkUsername():
  username = request.json['username']
  found = dbHandler.checkIfUsernameExists(username)
  return {'status': 200, 'found': found}


@app.route('/getRoles')
def flask_getRoles():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 403})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 401}
  roles = dbHandler.getAllRoles()
  return {'status': 200, 'roles': roles}

@app.route('/createPerson', methods=['POST'])
def flask_createPerson():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 403})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 401}
    fname = request.json['firstName']
    lname = request.json['lastName']
    birthNum = int(request.json['birthNumber'].replace('/', ''))
    roleId = request.json['roleId']
    dbHandler.addPerson(birthNum, roleId, fname, lname)
    return {'status': 200}
  return {'status': 403}

@app.route('/createAccount', methods=['POST'])
def flask_createAccount():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 403})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 401}
    username = request.json['username']
    password = request.json['password']
    birthNumber = dbHandler.getPersonByBirthNumber(int(request.json['birthNumber'].replace('/', '')))[0]
    dbHandler.addAccount(birthNumber, username, password)
    return {'status': 200}
  return {'status': 403}

@app.route('/createBuilding', methods=['POST'])
def flask_createBuilding():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 403})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 401}
    name = request.json['name']
    strId = request.json['strId']
    dbHandler.addBuilding(name, strId)
    return {'status': 200}
  return {'status': 403}

@app.route('/getBuildings')
def flask_getBuildings():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 403})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 401}
  buildings = dbHandler.getAllBuildings()
  return {'status': 200, 'buildings': buildings}

@app.route('/createClassroom', methods=['POST'])
def flask_createClassroom():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 403})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 401}
    number = request.json['number']
    capacity = request.json['capacity']
    buildingId = request.json['buildingId']
    dbHandler.addClassroom(number, capacity, buildingId)
    return {'status': 200}
  return {'status': 403}



def main():
  dbHandler.initializeAll()
  admin = dbHandler.getPersonByBirthNumber(0)
  if not admin:
    dbHandler.addPerson(0, 1, 'admin', 'admin')
    dbHandler.addAccount(1, 'admin', 'admin')
  app.run(port=5000)#, ssl_context=('cert.pem', 'key.pem'))


if __name__ == '__main__':
  main()
