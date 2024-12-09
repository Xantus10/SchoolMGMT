from datetime import datetime, timedelta
from flask import Flask, request, make_response
from flask_cors import CORS

from dbHandler import DbHandler
from MyJWT import JWT


COOKIEEXPIRYSECONDS = 24 * 3600 # 1 day
jwt = JWT()
jwt.set_secret_key('v4t13G*N-HJQ5v+173Y5+.vEbpV^BGGH60[R<8Ev63V*D+5Aa4eQ5tva]}')
jwt.set_expires(COOKIEEXPIRYSECONDS)

dbHandler = DbHandler('data/database.db')

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
    if uid == -1: return {'status': 401}
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
  return{'status': 401}


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
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  roles = dbHandler.getAllRoles()
  return {'status': 200, 'roles': roles}

@app.route('/createPerson', methods=['POST'])
def flask_createPerson():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    fname = request.json['firstName'].capitalize()
    lname = request.json['lastName'].capitalize()
    birthNum = int(request.json['birthNumber'].replace('/', ''))
    roleId = request.json['roleId']
    code = dbHandler.addPerson(birthNum, roleId, fname, lname)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Birth number already in use!'
      case dbHandler.ERR_FK:
        msg = 'Invalid role!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/createAccount', methods=['POST'])
def flask_createAccount():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    username = request.json['username']
    password = request.json['password']
    birthNumber = dbHandler.getPersonByBirthNumber(int(request.json['birthNumber'].replace('/', '')))
    birthNumber = birthNumber[0] if birthNumber else -1
    code = dbHandler.addAccount(birthNumber, username, password)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Username already in use!'
      case dbHandler.ERR_PK:
        msg = 'Person already owns an account'
      case dbHandler.ERR_FK:
        msg = 'Person for provided birth number was not found!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/createBuilding', methods=['POST'])
def flask_createBuilding():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    name = request.json['name']
    strId = request.json['strId']
    code = dbHandler.addBuilding(name, strId)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Building name or strID already exists!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getBuildings')
def flask_getBuildings():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  buildings = dbHandler.getAllBuildings()
  return {'status': 200, 'buildings': buildings}

@app.route('/createClassroom', methods=['POST'])
def flask_createClassroom():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    number = request.json['number']
    capacity = request.json['capacity']
    buildingId = request.json['buildingId']
    code = dbHandler.addClassroom(number, capacity, buildingId)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Classroom with specified number already exists in building!'
      case dbHandler.ERR_FK:
        msg = 'Invalid building provided!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/createCourse', methods=['POST'])
def flask_createCourse():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    name = request.json['name']
    strId = request.json['strId']
    code = dbHandler.addCourse(name, strId)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Course name or strID already exists!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/createRole', methods=['POST'])
def flask_createRole():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    role = request.json['role'].lower()
    code = dbHandler.addRole(role)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Role already exists!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getPeopleByNames')
def flask_getPeopleByNames():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  fn = request.args.get('firstName')
  ln = request.args.get('lastName')
  fn = fn.capitalize() if fn else None
  ln = ln.capitalize() if ln else None
  people = dbHandler.getAllPeopleWithName(fn, ln)
  return {'status': 200, 'people': people}

@app.route('/getEmployeesByNames')
def flask_getEmployeesByNames():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  fn = request.args.get('firstName')
  ln = request.args.get('lastName')
  fn = fn.capitalize() if fn else None
  ln = ln.capitalize() if ln else None
  employees = dbHandler.getAllEmployeesWithName(fn, ln)
  return {'status': 200, 'employees': employees}

@app.route('/createEmployee', methods=['POST'])
def flask_createEmployee():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    personId = request.json['personId']
    withSupervisor = request.json['withSupervisor']
    supervisorId = request.json['supervisorId'] if withSupervisor else None
    code = dbHandler.addEmployee(personId, supervisorId)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_PK:
        msg = 'Person is already an employee'
      case dbHandler.ERR_FK:
        msg = 'Person was not found or selected supervisor is not an employee'
      case dbHandler.ERR_CHECK:
        msg = 'Person cannot have itself as a supervisor, uncheck "has supervisor" for a person without supervisor'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getTeacherByStrId')
def flask_getTeacherByStrId():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  sid = request.args.get('strId')
  sid = sid.upper() if sid else None
  teacher = dbHandler.getTeacherByStrId(sid)
  return {'status': 200, 'teacher': teacher}

@app.route('/createTeacher', methods=['POST'])
def flask_createTeacher():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    personId = request.json['personId']
    strId = request.json['strId']
    strId = strId.upper() if strId else None
    teachingFrom = request.json['teachingFrom']
    teachingFrom = teachingFrom[0:10] if teachingFrom else None
    code = dbHandler.addTeacher(personId, teachingFrom, strId)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Identificator already exists'
      case dbHandler.ERR_PK:
        msg = 'Person is already a teacher'
      case dbHandler.ERR_FK:
        msg = 'Person is not an employee'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getCourses')
def flask_getCourses():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  courses = dbHandler.getAllCourses()
  return {'status': 200, 'courses': courses}

@app.route('/getClassroomId')
def flask_getClassrooms():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  buildingId = request.args.get('buildingId')
  classroomNumber = request.args.get('classroomNumber')
  classroom = dbHandler.getClassroomId(classroomNumber, buildingId)
  return {'status': 200, 'classroom': classroom}

@app.route('/createClass', methods=['POST'])
def flask_createClass():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    courseId = request.json['courseId']
    startYear = request.json['startYear']
    rootClassroomId = request.json['rootClassroomId']
    classTeacherId = request.json['classTeacherId']
    groupNumber = request.json['groupNumber'] if request.json['groupNumber'] in (1, 2) else None
    code = dbHandler.addClass(courseId, startYear, rootClassroomId, classTeacherId, groupNumber)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Class already exists OR classroom is already occupied'
      case dbHandler.ERR_FK:
        msg = 'Person is not employee OR classroom does not exist'
      case dbHandler.ERR_CHECK:
        msg = 'Start year must be between 2000 and 9999'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getClasses')
def flask_getClasses():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  classes = dbHandler.getAllClasses()
  return {'status': 200, 'classes': classes}

@app.route('/createStudent', methods=['POST'])
def flask_createStudent():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    personId = request.json['personId']
    classId = request.json['classId']
    half = request.json['half']
    code = dbHandler.addStudent(personId, classId, half)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_PK:
        msg = 'Person is already a student'
      case dbHandler.ERR_FK:
        msg = 'Person or class do not exist'
      case dbHandler.ERR_CHECK:
        msg = 'Half must be either \'A\' or \'B\''
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/createSubject', methods=['POST'])
def flask_createSubject():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    name = request.json['name']
    strId = request.json['strId']
    code = dbHandler.addSubject(name, strId)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Subject name or strID already exists!'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getSubjects')
def flask_getSubjects():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  subjects = dbHandler.getAllSubjects()
  return {'status': 200, 'subjects': subjects}

@app.route('/getSubjectsExpertiseForTeacher')
def flask_getSubjectsForTeacher():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  teacherId = request.args.get('teacherId')
  subjects = dbHandler.getAllExpertiseWithTeacher(teacherId)
  return {'status': 200, 'subjects': subjects}

@app.route('/createTeacherSubject', methods=['POST'])
def flask_createTeacherSubject():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    teacherId = request.json['teacherId']
    subjectId = request.json['subjectId']
    code = 0
    i = 0
    while i < len(subjectId) and code == 0:
      code = dbHandler.addTeacherSubjectExpertise(teacherId, int(subjectId[i]))
      i += 1
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_PK:
        msg = 'Teacher already has an expertise in subject'
      case dbHandler.ERR_FK:
        msg = 'Teacher or subject do not exist'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/createLectureTime', methods=['POST'])
def flask_createLectureTime():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    lectureId = request.json['lectureId']
    time = request.json['time']
    if time:
      time = time.split(':')
      time = int(time[0])*60+int(time[1])
    code = dbHandler.addLectureTime(lectureId, time)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_PK:
        msg = 'Lecture already exists'
      case dbHandler.ERR_UNIQUE:
        msg = 'There is a lecture starting at that time'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/initializeLectures', methods=['POST'])
def flask_initializeLectures():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    code = dbHandler.initializeLectures()
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}

@app.route('/getLectureTimes')
def flask_getlectureTimes():
  JWT_token = request.cookies.get('JWT_token')
  JWT_user_context = request.cookies.get('JWT_user_context')
  isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
  if not isValid:
    resp = make_response({'status': 401})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp
  if data['role'] != 'admin': {'status': 403}
  times = dbHandler.getAllLectureTimes()
  return {'status': 200, 'times': times}

@app.route('/createSchedule', methods=['POST'])
def flask_createSchedule():
  if request.method == 'POST':
    JWT_token = request.cookies.get('JWT_token')
    JWT_user_context = request.cookies.get('JWT_user_context')
    isValid, data = jwt.jwtdecode(JWT_token, JWT_user_context)
    if not isValid:
      resp = make_response({'status': 401})
      resp.delete_cookie('JWT_token')
      resp.delete_cookie('JWT_user_context')
      return resp
    if data['role'] != 'admin': {'status': 403}
    lectureId = request.json['lectureId']
    classId = request.json['classId']
    teacherId = request.json['teacherId']
    subjectId = request.json['subjectId']
    classroomId = request.json['classroomId']
    FullOrAB = request.json['FullOrAB']
    code = dbHandler.addScheduleSingle(lectureId, classId, teacherId, subjectId, classroomId, FullOrAB)
    if code == 0: return {'status': 200}
    msg = ''
    match (code):
      case dbHandler.ERR_UNIQUE:
        msg = 'Insert failed, make sure, that\nTeacher isn\'t occupied or\nClassroom isn\'t occupied'
      case dbHandler.ERR_CHECK:
        msg = 'Invalid division modifier'
      case _:
        msg = f'Undefined database error, please report this issue with date: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} and code: {code}'
    return {'status': 500, 'msg': msg}
  return {'status': 401}



@app.route('/logout', methods=['POST'])
def flask_logout():
  if request.method == 'POST':
    resp = make_response({'status': 200})
    resp.delete_cookie('JWT_token')
    resp.delete_cookie('JWT_user_context')
    return resp

def main():
  dbHandler.initializeAll()
  admin = dbHandler.getPersonByBirthNumber(0)
  if not admin:
    dbHandler.addPerson(0, 1, 'admin', 'admin')
    dbHandler.addAccount(1, 'admin', 'admin')
  app.run(port=5000)#, ssl_context=('cert.pem', 'key.pem'))


if __name__ == '__main__':
  main()
