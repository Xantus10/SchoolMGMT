import datetime
import sqlite3
from bcrypt import gensalt, hashpw, checkpw
from itertools import product

from logs import Logger

class DbHandler:
  def __init__(self, dbLocation):
    self.logger = Logger()

    # ERROR CODES
    self.ERR_UNIQUE = 2067
    self.ERR_PK = 1555
    self.ERR_FK = 787
    self.ERR_CHECK = 275

    self.dbLocation = dbLocation

  
  def getDBConn(self):
    db = sqlite3.connect(self.dbLocation)
    db.execute('PRAGMA foreign_keys = ON;')
    return db


  # Initialize all database tables
  def initialize(self):
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('CREATE TABLE IF NOT EXISTS buildings(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS classrooms(id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER NOT NULL, capacity INTEGER NOT NULL, buildingId INTEGER NOT NULL, CONSTRAINT FK_classrooms_buildingId FOREIGN KEY (buildingId) REFERENCES buildings(id), CONSTRAINT U_classrooms_number_buildingId UNIQUE (number, buildingId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS roles(id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS names(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT, birthNumber INTEGER NOT NULL UNIQUE, roleId INTEGER NOT NULL, firstNameId INTEGER NOT NULL, lastNameId INTEGER NOT NULL, CONSTRAINT FK_people_roleId FOREIGN KEY (roleId) REFERENCES roles(id), CONSTRAINT FK_people_firstNameId FOREIGN KEY (firstNameId) REFERENCES names(id), CONSTRAINT FK_people_lastNameId FOREIGN KEY (lastNameId) REFERENCES names(id));')
      cursor.execute('CREATE TABLE IF NOT EXISTS accounts(personId INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, disabled INTEGER, CONSTRAINT FK_accounts_personId FOREIGN KEY (personId) REFERENCES people(id), CONSTRAINT CH_accounts_disabled CHECK (disabled IS NULL OR disabled=1));')
      cursor.execute('CREATE TABLE IF NOT EXISTS employees(personId INTEGER PRIMARY KEY, supervisorId INTEGER, CONSTRAINT FK_employees_personId FOREIGN KEY(personId) REFERENCES people(id), CONSTRAINT FK_employees_supervisorId FOREIGN KEY (supervisorId) REFERENCES employees(personId), CONSTRAINT CH_employees_supervisorId CHECK (supervisorId!=personId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS teachers(personId INTEGER PRIMARY KEY, strIdentifier TEXT NOT NULL UNIQUE, teachingFrom DATE NOT NULL, CONSTRAINT FK_teachers_personId FOREIGN KEY (personId) REFERENCES employees(personId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY AUTOINCREMENT, startYear INTEGER NOT NULL, groupNumber INTEGER NOT NULL, rootClassroomId INTEGER NOT NULL UNIQUE, courseId INTEGER NOT NULL, classTeacherId INTEGER NOT NULL, CONSTRAINT FK_classes_rootClassroomId FOREIGN KEY (rootClassroomId) REFERENCES classrooms(id), CONSTRAINT FK_classes_courseId FOREIGN KEY (courseId) REFERENCES courses(id), CONSTRAINT FK_classes_classTeacherId FOREIGN KEY (classTeacherId) REFERENCES teachers(personId), CONSTRAINT U_classes_startYear_courseId_groupNumber UNIQUE (startYear, courseId, groupNumber), CONSTRAINT CH_classes_groupNumber_startYear CHECK ((groupNumber>=0 AND groupNumber<=2) AND (startYear>2000 AND startYear<=9999)));')
      cursor.execute('CREATE TABLE IF NOT EXISTS students(personId INTEGER PRIMARY KEY, classId INTEGER NOT NULL, half TEXT NOT NULL, CONSTRAINT FK_students_personId FOREIGN KEY (personId) REFERENCES people(id), CONSTRAINT FK_students_classId FOREIGN KEY (classId) REFERENCES classes(id), CONSTRAINT CH_students_half CHECK (half=\'A\' OR half=\'B\'));')
      cursor.execute('CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS teachersSubjectsExpertise(teacherId INTEGER, subjectId INTEGER, CONSTRAINT PK_teachersSubjectsExpertise PRIMARY KEY (teacherId, subjectId), CONSTRAINT FK_teachersSubjectsExpertise_teacherId FOREIGN KEY (teacherId) REFERENCES teachers(personId), CONSTRAINT FK_teachersSubjectsExpertise_subjectId FOREIGN KEY (subjectId) REFERENCES subjects(id));')
      cursor.execute('CREATE TABLE IF NOT EXISTS daysInWeek(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS lectureTimes(id INTEGER PRIMARY KEY, startTime INTEGER NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS lectures(id INTEGER PRIMARY KEY AUTOINCREMENT, isEvenWeek INTEGER NOT NULL, dayId INTEGER NOT NULL, timeId INTEGER NOT NULL, CONSTRAINT FK_lectures_dayId FOREIGN KEY (dayId) REFERENCES daysInWeek(id), CONSTRAINT FK_lectures_timeId FOREIGN KEY (timeId) REFERENCES lectureTimes(id), CONSTRAINT U_lectures_all UNIQUE (isEvenWeek, dayId, timeId), CONSTRAINT CH_lectures_isEvenWeek CHECK (isEvenWeek=0 OR isEvenWeek=1));')
      cursor.execute('CREATE TABLE IF NOT EXISTS schedules(id INTEGER PRIMARY KEY AUTOINCREMENT, lectureId INTEGER NOT NULL, classId INTEGER NOT NULL, teacherId INTEGER NOT NULL, subjectId INTEGER NOT NULL, fullOrAB TEXT NOT NULL, classroomId INTEGER NOT NULL, CONSTRAINT FK_schedules_lectureId FOREIGN KEY (lectureId) REFERENCES lectures(id), CONSTRAINT FK_schedules_classId FOREIGN KEY (classId) REFERENCES classes(id), CONSTRAINT FK_schedules_teachersubjectId FOREIGN KEY (teacherId, subjectId) REFERENCES teachersSubjectsExpertise(teacherId, subjectId), CONSTRAINT FK_schedules_classroomId FOREIGN KEY (classroomId) REFERENCES classrooms(id), CONSTRAINT U_schedules_lectureId_classId_fullOrAB UNIQUE(lectureId, classId, fullOrAB), CONSTRAINT U_schedules_lectureId_teacherId UNIQUE(lectureId, teacherId), CONSTRAINT U_schedules_lectureId_classroomId UNIQUE(lectureId, classroomId), CONSTRAINT CH_schedules_fullOrAB CHECK (fullOrAB=\'A\' OR fullOrAB=\'B\' OR fullOrAB=\'F\'));')
      cursor.execute('CREATE TABLE IF NOT EXISTS classification(id INTEGER PRIMARY KEY AUTOINCREMENT, weight REAL NOT NULL, date DATE NOT NULL, title TEXT NOT NULL, scheduleId INTEGER NOT NULL, CONSTRAINT FK_classification_scheduleId FOREIGN KEY (scheduleId) REFERENCES schedules(id), CONSTRAINT U_classification_scheduleId_date_title UNIQUE (scheduleId, date, title), CONSTRAINT CH_classification_weight CHECK (weight>0 AND weight<=1));')
      cursor.execute('CREATE TABLE IF NOT EXISTS studentMarks(id INTEGER PRIMARY KEY AUTOINCREMENT, mark REAL NOT NULL, studentId INTEGER NOT NULL, comment TEXT, classificationId INTEGER NOT NULL, CONSTRAINT FK_classification_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_classification_classificationId FOREIGN KEY (classificationId) REFERENCES classification(id), CONSTRAINT U_studentMarks_studentId_classificationId UNIQUE (studentId, classificationId), CONSTRAINT CH_studentMarks_mark CHECK (mark>=1 AND mark<=5 AND (mark%0.5)=0.0));')
      cursor.execute('CREATE TABLE IF NOT EXISTS studentComments(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE NOT NULL, studentId INTEGER NOT NULL, teacherId INTEGER NOT NULL, comment TEXT NOT NULL, CONSTRAINT FK_studentComments_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_studentComments_teacherId FOREIGN KEY (teacherId) REFERENCES teachers(personId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS absenceTypes(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS studentsAbsence(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE NOT NULL, lectureId INTEGER NOT NULL, studentId INTEGER NOT NULL, absenceTypeId INTEGER NOT NULL, CONSTRAINT FK_studentsAbsence_lectureId FOREIGN KEY (lectureId) REFERENCES lectures(id), CONSTRAINT FK_studentsAbsence_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_studentsAbsence_absenceTypeId FOREIGN KEY (absenceTypeId) REFERENCES absenceTypes(id), CONSTRAINT U_studentsAbsence_date_lectureId_studentId UNIQUE (date, lectureId, studentId));')
    except sqlite3.Error as e:
      self.logger.logsqlite('initializing tables', 0, e)
    except Exception as e:
      self.logger.logunexpected('initializing tables', e)
    db.commit()
    return 0


  # Add a building with specified parameters
  def addBuilding(self, name: str, strIdentifier: str):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO buildings(name, strIdentifier) VALUES(?, ?);', (name, strIdentifier))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a building', e, e.sqlite_errorcode, (name, strIdentifier))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a building', e)
    db.commit()
    return 0

  def getAllBuildings(self) -> list[list[int, str, str]]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      building = cursor.execute('SELECT * FROM buildings;')
      building = building.fetchall()
      db.commit()
      return building
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all buildings', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all buildings', e)
    db.commit()
    return []

  # [id, name, strID]
  def getBuildingByName(self, name: str) -> list[int, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      building = cursor.execute('SELECT * FROM buildings WHERE name=?;', (name,))
      building = building.fetchone()
      db.commit()
      if building:
        return building
      self.logger.log(f'Building was not found for name {name}', 2)
      return []
    except sqlite3.Error as e:
      self.logger.logsqlite('getting a building', e, e.sqlite_errorcode, (name))
    except Exception as e:
      self.logger.logunexpected('getting a building', e)
    db.commit()
    return []

  # [id, name, strID]
  def getBuildingById(self, buildingId: int) -> list[int, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      building = cursor.execute('SELECT * FROM buildings WHERE id=?;', (buildingId,))
      building = building.fetchone()
      db.commit()
      if building:
        return building
      self.logger.log(f'Building was not found for id {buildingId}', 2)
      return []
    except sqlite3.Error as e:
      self.logger.logsqlite('getting a building', e, e.sqlite_errorcode, (buildingId))
    except Exception as e:
      self.logger.logunexpected('getting a building', e)
    db.commit()
    return []



  def addClassroom(self, number: int, capacity: int, buildingId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO classrooms(number, capacity, buildingId) VALUES(?, ?, ?);', (number, capacity, buildingId))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a classroom', e, e.sqlite_errorcode, (number, capacity, buildingId))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a classroom', e)
    db.commit()
    return 0

  # [id, number, capacity]
  def getAllClassroomsForBuilding(self, buildingId: int) -> list[list[int, int, int]]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      classrooms = cursor.execute('SELECT * FROM classrooms WHERE buildingId=?;', (buildingId,))
      classrooms = classrooms.fetchall()
      db.commit()
      return classrooms
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all classrooms', e, e.sqlite_errorcode, buildingId)
    except Exception as e:
      self.logger.logunexpected('getting all classrooms', e)
    db.commit()
    return []

  def getClassroomId(self, number: int, buildingId: int) -> int:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      classrooms = cursor.execute('SELECT * FROM classrooms WHERE number=? AND buildingId=?;', (number, buildingId))
      classrooms = classrooms.fetchone()
      db.commit()
      return classrooms
    except sqlite3.Error as e:
      self.logger.logsqlite('getting classroomId', e, e.sqlite_errorcode, (number, buildingId))
    except Exception as e:
      self.logger.logunexpected('getting classroomId', e)
    db.commit()
    return []



  def addCourse(self, name: str, strId: str):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO courses(name, strIdentifier) VALUES(?, ?);', (name, strId))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a course', e, e.sqlite_errorcode, (name, strId))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a course', e)
    db.commit()
    return 0

  def getAllCourses(self):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      courses = cursor.execute('SELECT * FROM courses;')
      courses = courses.fetchall()
      db.commit()
      return courses
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all courses', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all courses', e)
    db.commit()
    return []


  # Initialize basic roles (admin, teacher, student)
  def initializeRoles(self):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      default = [('admin',), ('teacher',), ('student',)]
      cursor.executemany('INSERT OR IGNORE INTO roles(role) VALUES(?);', default)
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a role', e, e.sqlite_errorcode, (default))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a role', e)
    db.commit()
    return 0

  def addRole(self, role: str):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      role = role.lower()
      cursor.execute('INSERT INTO roles(role) VALUES(?);', (role,))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a role', e, e.sqlite_errorcode, (role))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a role', e)
    db.commit()
    return 0

  def getAllRoles(self):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      roles = cursor.execute('SELECT * FROM roles;')
      roles = roles.fetchall()
      db.commit()
      return roles
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all roles', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all roles', e)
    db.commit()
    return []



  def addPerson(self, birthNumber: int, roleId: int, firstName: str, lastName: str):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT OR IGNORE INTO names(name) VALUES(?)', (firstName,))
      cursor.execute('INSERT OR IGNORE INTO names(name) VALUES(?)', (lastName,))
      fnId = cursor.execute('SELECT id FROM names WHERE name=?', (firstName,))
      fnId = fnId.fetchone()[0]
      lnId = cursor.execute('SELECT id FROM names WHERE name=?', (lastName,))
      lnId = lnId.fetchone()[0]
      cursor.execute('INSERT INTO people(birthNumber, roleId, firstNameId, lastNameId) VALUES(?, ?, ?, ?)', (birthNumber, roleId, fnId, lnId))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a person', e, e.sqlite_errorcode, (birthNumber, roleId, firstName, lastName))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a person', e)
    db.commit()
    return 0

  # [id, role, fname, lname]
  def getPersonByBirthNumber(self, birthNumber: int) -> list[int, str, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      person = cursor.execute('''SELECT people.id, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE people.birthNumber=?;''', (birthNumber,))
      person = person.fetchone()
      db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.logsqlite('getting person(bn)', e, e.sqlite_errorcode, birthNumber)
    except Exception as e:
      self.logger.logunexpected('getting person(bn)', e)
    db.commit()
    return []

  # [birthNumber, role, fname, lname]
  def getPersonById(self, pid: int) -> list[int, str, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      person = cursor.execute('''SELECT people.birthNumber, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE people.id=?;''', (pid,))
      person = person.fetchone()
      db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.logsqlite('getting person(id)', e, e.sqlite_errorcode, pid)
    except Exception as e:
      self.logger.logunexpected('getting person(id)', e)
    db.commit()
    return []

  # [id, birthNumber, role, fname, lname]
  def getAllPeopleWithName(self, firstName: str='', lastName: str='') -> list[list[int, int, str, str, str]]:
    try:
      if not firstName and not lastName: return []
      
      db = self.getDBConn()
      cursor = db.cursor()
      data = ()
      if firstName and lastName:
        data = (firstName+'%', lastName+'%')
      else:
        data = (firstName+'%',) if firstName else (lastName+'%',)
      person = cursor.execute(f'''SELECT people.id, people.birthNumber, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE {"fn.name LIKE ?" if firstName else ""} {"AND" if firstName and lastName else ""} {"ln.name LIKE ?" if lastName else ""};''', data)
      person = person.fetchall()
      db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all people by role', e, e.sqlite_errorcode, firstName, lastName)
    except Exception as e:
      self.logger.logunexpected('getting all people by name', e)
    db.commit()
    return []

  # [id, birthNumber, fname, lname]
  def getAllPeopleWithRole(self, role: str) -> list[list[int, int, str, str]]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      person = cursor.execute('''SELECT people.id, people.birthNumber, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE roles.role=?;''', (role,))
      person = person.fetchall()
      db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all people by role', e, e.sqlite_errorcode, role)
    except Exception as e:
      self.logger.logunexpected('getting all people by role', e)
    db.commit()
    return []


  def addAccount(self, personId: int, username: str, password: str):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      # Hash the password
      hashed = hashpw(bytes(password, 'utf-8'), gensalt())
      # Data for INSERT
      data = (personId, username, hashed)
      # INSERT into accounts table
      cursor.execute('INSERT INTO accounts(personId, username, password) VALUES(?, ?, ?);', data)
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a user', e, e.sqlite_errorcode, (personId, username, password))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a user', e)
    db.commit()
    return 0

  def getAccountInfoById(self, personId: int) -> list[str, bool]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      account = cursor.execute('SELECT username, disabled FROM accounts WHERE personId=?;', (personId,))
      account = list(account.fetchone())
      db.commit()
      if account: account[1] = bool(account[1])
      return account
    except sqlite3.Error as e:
      self.logger.logsqlite('getting account', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting account', e)
    db.commit()
    return []


  # Check if inserting the row with specified pid and sid will cause a loop where pid is super of sid and sid is super of pid
  def checkForSupervisorLoop(self, personId: int, supervisorId: int) -> bool:
    try:
        
      db = self.getDBConn()
      cursor = db.cursor()
      # Get supervisor
      sup = cursor.execute('SELECT * FROM employees WHERE personId=?', (supervisorId,))
      sup = sup.fetchone()
      db.commit()
      if sup: return sup[1] == personId
    except sqlite3.Error as e:
      self.logger.logsqlite('checking supervisor loops', e, e.sqlite_errorcode, (personId, supervisorId))
    except Exception as e:
      self.logger.logunexpected('checking supervisor loops', e)
    db.commit()
    return 0

  def addEmployee(self, personId: int, supervisorId: int=None):
    try:
        
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO employees(personId, supervisorId) VALUES(?, ?);', (personId, supervisorId))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding an employee', e, e.sqlite_errorcode, (personId, supervisorId))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding an employee', e)
    db.commit()
    return 0

  def getEmployeeById(self, personId: int) -> list[int, int]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      emp = cursor.execute('SELECT * FROM employees WHERE;')
      emp = emp.fetchall()
      db.commit()
      return emp
    except sqlite3.Error as e:
      self.logger.logsqlite('getting employee', e, e.sqlite_errorcode, personId)
    except Exception as e:
      self.logger.logunexpected('getting employee', e)
    db.commit()
    return []

  # [id, role, fname, lname]
  def getAllEmployeesWithSupervisor(self, supervisorId: int) -> list[int, str, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      person = cursor.execute('''SELECT people.id, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  JOIN employees ON employees.personId=people.id
                                                  WHERE employees.supervisorId=?;''', (supervisorId,))
      person = person.fetchall()
      db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all employees by supervisor', e, e.sqlite_errorcode, supervisorId)
    except Exception as e:
      self.logger.logunexpected('getting all employees by supervisor', e)
    db.commit()
    return []

  def getAllEmployeesWithName(self, firstName: str='', lastName: str='') -> list[list[int, int, str, str, str]]:
    try:
      if not firstName and not lastName: return []
      
      db = self.getDBConn()
      cursor = db.cursor()
      data = ()
      if firstName and lastName:
        data = (firstName+'%', lastName+'%')
      else:
        data = (firstName+'%',) if firstName else (lastName+'%',)
      person = cursor.execute(f'''SELECT people.id, people.birthNumber, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  JOIN employees ON employees.personId=people.id
                                                  WHERE {"fn.name LIKE ?" if firstName else ""} {"AND" if firstName and lastName else ""} {"ln.name LIKE ?" if lastName else ""};''', data)
      person = person.fetchall()
      db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all employees by name', e, e.sqlite_errorcode, firstName, lastName)
    except Exception as e:
      self.logger.logunexpected('getting all employees by name', e)
    db.commit()
    return []


  def addTeacher(self, personId: int, teachingFrom: datetime.date, strIdentifier: str):
    try:
        
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO teachers(personId, teachingFrom, strIdentifier) VALUES(?, ?, ?);', (personId, teachingFrom, strIdentifier))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a teacher', e, e.sqlite_errorcode, (personId, teachingFrom, strIdentifier))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a teacher', e)
    db.commit()
    return 0

  # [id, fname, lname, strID, teachFrom]
  def getAllTeachers(self) -> list[int, str, str, str, datetime.datetime]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      teachers = cursor.execute('''SELECT people.id, fn.name, ln.name, teachers.strIdentifier, teachers.teachingFrom FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  JOIN teachers ON teachers.personId=people.id;''')
      teachers = teachers.fetchall()
      db.commit()
      for i, teacher in enumerate(teachers):
        teachers[i] = list(teacher)
        teachers[i][-1] = datetime.datetime.strptime(teachers[i][-1], '%Y-%m-%d')
      return teachers
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all teachers', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all teachers', e)
    db.commit()
    return []

  # [id, fname, lname, teachFrom]
  def getTeacherByStrId(self, strId: str) -> list[int, str, str, datetime.datetime]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      teachers = cursor.execute('''SELECT people.id, fn.name, ln.name, teachers.teachingFrom FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN teachers ON teachers.personId=people.id
                                                  WHERE teachers.strIdentifier=?;''', (strId,))
      teachers = teachers.fetchone()
      db.commit()
      return teachers
    except sqlite3.Error as e:
      self.logger.logsqlite('getting a teacher', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting a teacher', e)
    db.commit()
    return []


  def addClass(self, courseId: int, startYear: int, rootClassroomId: int, classTeacherId: int, groupNumber: int=0):
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO classes(startYear, rootClassroomId, courseId, classTeacherId, groupNumber) VALUES(?, ?, ?, ?, ?);', (startYear, rootClassroomId, courseId, classTeacherId, groupNumber))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a class', e, e.sqlite_errorcode, (startYear, rootClassroomId, courseId, classTeacherId, groupNumber))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a class', e)
    db.commit()
    return 0

  # [id, courseStrID, startYear, groupNumber, classTeacherId, rootClassroomId]
  def getAllClasses(self) -> list[int, str, int, int, int, int]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      classes = cursor.execute('''SELECT classes.id, courses.strIdentifier, classes.startYear, classes.groupNumber, classes.classTeacherId, classes.rootClassroomId FROM classes
                                                  JOIN courses ON courses.id=classes.courseId;''')
      classes = classes.fetchall()
      db.commit()
      return classes
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all classes', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all classes', e)
    db.commit()
    return []

  # [id, courseStrID, startYear, groupNumber, rootClassroomId]
  def getAllClassesWithTeacher(self, classTeacherId: int) -> list[int, str, int, int, int]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      classes = cursor.execute('''SELECT classes.id, courses.strIdentifier, classes.startYear, classes.groupNumber, classes.rootClassroomId FROM classes
                                                  JOIN courses ON courses.id=classes.courseId
                                                  WHERE classes.classTeacherId=?;''', (classTeacherId,))
      classes = classes.fetchall()
      db.commit()
      return classes
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all classes', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all classes', e)
    db.commit()
    return []



  def addStudent(self, personId: int, classId: int, half: str):
    try:
        
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO students(personId, classId, half) VALUES(?, ?, ?);', (personId, classId, half))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a student', e, e.sqlite_errorcode, (personId, classId, half))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a student', e)
    db.commit()
    return 0

  # [id, fname, lname, half]
  def getAllStudentsWithOptClassHalf(self, classId: int, half: str=None) -> list[int, str, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      data = (classId, half) if half else (classId,)
      students = cursor.execute(f'''SELECT people.id, fn.name, ln.name, students.half FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN students ON students.personId=people.id
                                                  WHERE students.classId=?{" AND students.half=?" if half else ""};''', data)
      students = students.fetchall()
      db.commit()
      return students
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all students', e, e.sqlite_errorcode, (classId, half))
    except Exception as e:
      self.logger.logunexpected('getting all students', e)
    db.commit()
    return []



  def addSubject(self, name: str, strIdentifier: str):
    try:
        
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO subjects(name, strIdentifier) VALUES(?, ?);', (name, strIdentifier))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a subject', e, e.sqlite_errorcode, (name, strIdentifier))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a subject', e)
    db.commit()
    return 0

  # [id, name, strID]
  def getAllSubjects(self) -> list[int, str, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      subjects = cursor.execute('SELECT * FROM subjects;')
      subjects = subjects.fetchall()
      db.commit()
      return subjects
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all subjects', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all subjects', e)
    db.commit()
    return []



  def addTeacherSubjectExpertise(self, teacherId: int, subjectId: int):
    try:
        
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO teachersSubjectsExpertise(teacherId, subjectId) VALUES(?, ?);', (teacherId, subjectId))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a teacher subject', e, e.sqlite_errorcode, (teacherId, subjectId))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a teacher subject', e)
    db.commit()
    return 0

  # [id, strID]
  def getAllExpertiseWithTeacher(self, teacherId: int) -> list[int, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      expertise = cursor.execute('''SELECT subjects.id, subjects.strIdentifier FROM teachersSubjectsExpertise
                                                  JOIN subjects ON teachersSubjectsExpertise.subjectId=subjects.id
                                                  WHERE teachersSubjectsExpertise.teacherId=?''', (teacherId,))
      expertise = expertise.fetchall()
      db.commit()
      return expertise
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all expertise(t)', e, e.sqlite_errorcode, (teacherId))
    except Exception as e:
      self.logger.logunexpected('getting all expertise(t)', e)
    db.commit()
    return []

  # [id, strID]
  def getAllExpertiseWithSubject(self, subjectId: int) -> list[int, str]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      expertise = cursor.execute('''SELECT teachers.personId, teachers.strIdentifier FROM teachersSubjectsExpertise
                                                  JOIN teachers ON teachers.personId=teachersSubjectsExpertise.teacherId
                                                  WHERE teachersSubjectsExpertise.subjectId=?;''', (subjectId,))
      expertise = expertise.fetchall()
      db.commit()
      return expertise
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all expertise(s)', e, e.sqlite_errorcode, (subjectId))
    except Exception as e:
      self.logger.logunexpected('getting all expertise(s)', e)
    db.commit()
    return []



  def initializeDaysInWeek(self):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      days = [(1,'Mon'), (2,'Tue'), (3,'Wed'), (4,'Thu'), (5,'Fri'), (6,'Sat'), (7,'Sun')]
      cursor.executemany('INSERT OR IGNORE INTO daysInWeek(id, name) VALUES(?, ?);', days)
    except sqlite3.Error as e:
      self.logger.logsqlite('initializing daysInWeek', e, e.sqlite_errorcode)
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('initializing daysInWeek', e)
    db.commit()
    return 0

  # [id, Name]
  def getAllDaysInWeek(self) -> list[int, str]:
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      days = cursor.execute('SELECT * FROM daysInWeek;')
      days = days.fetchall()
      db.commit()
      return days
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all days', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all days', e)
    db.commit()
    return []

  def addLectureTime(self, lectureId: int, minutesAfterMidnight: int):
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO lectureTimes(id, startTime) VALUES(?, ?);', (lectureId, minutesAfterMidnight))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding lectureTime', e, e.sqlite_errorcode, (lectureId, minutesAfterMidnight))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding lectureTime', e)
    db.commit()
    return 0

  # [id, timestamp]
  def getAllLectureTimes(self) -> list[int, int]:
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      times = cursor.execute('SELECT * FROM lectureTimes;')
      times = times.fetchall()
      db.commit()
      return times
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all lecturetimes', e, e.sqlite_errorcode)
    except Exception as e:
      self.logger.logunexpected('getting all lecturetimes', e)
    db.commit()
    return []

  def initializeLectures(self):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      days = cursor.execute('SELECT id FROM daysInWeek;')
      days = days.fetchall()
      times = cursor.execute('SELECT id FROM lectureTimes;')
      times = times.fetchall()
      for i in range(len(days)):
        days[i] = days[i][0]
      for i in range(len(times)):
        times[i] = times[i][0]
      cursor.executemany('INSERT OR IGNORE INTO lectures(isEvenWeek, dayId, timeId) VALUES(?, ?, ?);', list(product([0,1], days, times)))
    except sqlite3.Error as e:
      self.logger.logsqlite('initializing lectures', e, e.sqlite_errorcode)
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('initializing lectures', e)
    db.commit()
    return 0

  # [id, dayId, timeId, isevenweek]
  def getAllLectures(self) -> list[int, str, datetime.datetime, bool]:
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      lectures = cursor.execute('''SELECT id, dayId, timeId, isEvenWeek FROM lectures;''')
      lectures = lectures.fetchall()
      db.commit()
      return lectures
    except sqlite3.Error as e:
      self.logger.logsqlite('getting all lectures', e)
    except Exception as e:
      self.logger.logunexpected('getting all lectures', e)
    db.commit()
    return []



  def addScheduleSingle(self, lectureId: int, classId: int, teacherId: int, subjectId: int, classroomId: int, FullORAB: str):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO schedules(lectureId, classId, teacherId, subjectId, classroomId, FullORAB) VALUES(?, ?, ?, ?, ?, ?);', (lectureId, classId, teacherId, subjectId, classroomId, FullORAB))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding schedule single', e, e.sqlite_errorcode, (lectureId, classId, teacherId, subjectId, classroomId, FullORAB))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding schedule single', e)
    db.commit()
    return 0

  # [lectureId, dayId, timeId, evenWeek, teacherStrID, subjectStrID, buildingStrID, classroomNum, fullOrAB]
  def getScheduleForClass(self, classId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      schedule = cursor.execute('''SELECT lectures.id, lectures.dayId, lectures.timeId, lectures.isEvenWeek, teachers.strIdentifier, subjects.strIdentifier, buildings.strIdentifier, classrooms.number, schedules.fullOrAB FROM schedules
                                                  JOIN lectures ON schedules.lectureId=lectures.id
                                                  JOIN teachers ON schedules.teacherId=teachers.personId
                                                  JOIN subjects ON schedules.subjectId=subjects.id
                                                  JOIN classrooms ON schedules.classroomId=classrooms.id
                                                  JOIN buildings ON classrooms.buildingId=buildings.id
                                                  WHERE schedules.classId=?;''', (classId,))
      schedule = schedule.fetchall()
      db.commit()
      return schedule
    except sqlite3.Error as e:
      self.logger.logsqlite('getting schedule for class', e)
    except Exception as e:
      self.logger.logunexpected('getting schedule for class', e)
    db.commit()
    return []

  # [lectureId, dayId, timeId, evenWeek, courseStrID, classStartYear, classGroupNumber, subjectStrID, buildingStrID, classroomNum, fullOrAB]
  def getScheduleForTeacher(self, teacherId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      schedule = cursor.execute('''SELECT lectures.id, lectures.dayId, lectures.timeId, lectures.isEvenWeek, courses.strIdentifier, classes.startYear, classes.groupNumber, subjects.strIdentifier, buildings.strIdentifier, classrooms.number, schedules.fullOrAB FROM schedules
                                                  JOIN lectures ON schedules.lectureId=lectures.id
                                                  JOIN classes ON schedules.classId=classes.id
                                                  JOIN courses ON classes.courseId=courses.id
                                                  JOIN subjects ON schedules.subjectId=subjects.id
                                                  JOIN classrooms ON schedules.classroomId=classrooms.id
                                                  JOIN buildings ON classrooms.buildingId=buildings.id
                                                  WHERE schedules.teacherId=?;''', (teacherId,))
      schedule = schedule.fetchall()
      db.commit()
      return schedule
    except sqlite3.Error as e:
      self.logger.logsqlite('getting schedule for teacher', e)
    except Exception as e:
      self.logger.logunexpected('getting schedule for teacher', e)
    db.commit()
    return []

  # [lectureId, dayId, timeId, evenWeek, courseStrID, classStratYear, classGroupNumber, subjectStrID, teacherStrID, fullOrAB]
  def getScheduleForClassroom(self, classroomId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      schedule = cursor.execute('''SELECT lectures.id, lectures.dayId, lectures.timeId, lectures.isEvenWeek, courses.strIdentifier, classes.startYear, classes.groupNumber, subjects.strIdentifier, teachers.strIdentifier, schedules.fullOrAB FROM schedules
                                                  JOIN lectures ON schedules.lectureId=lectures.ids
                                                  JOIN classes ON schedules.classId=classes.id
                                                  JOIN courses ON classes.courseId=courses.id
                                                  JOIN subjects ON schedules.subjectId=subjects.id
                                                  JOIN teachers ON schedules.teacherId=teachers.personId
                                                  WHERE schedules.classroomId=?;''', (classroomId,))
      schedule = schedule.fetchall()
      db.commit()
      return schedule
    except sqlite3.Error as e:
      self.logger.logsqlite('getting schedule for classroom', e)
    except Exception as e:
      self.logger.logunexpected('getting schedule for classroom', e)
    db.commit()
    return []

  # Add classification
  def addClassification(self, weight: float, dateOfMark: datetime.date, title: str, scheduleId: int):
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO classification(weight, date, title, scheduleId) VALUES(?, ?, ?, ?);', (weight, dateOfMark, title, scheduleId))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a classification', e, e.sqlite_errorcode, (weight, dateOfMark, title, scheduleId))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a classification', e)
    db.commit()
    return 0

  # [id, weight, date, title, dayId, timeId]
  def getAllClassificationForClass(self, classId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      classification = cursor.execute('''SELECT c.weight, c.date, c.title, l.dayId, l.timeId FROM schedules
                                    JOIN classification as c ON classification.scheduleId=schedules.id
                                    JOIN lectures as l ON schedules.lectureId=lectures.id
                                    WHERE schedules.classId=?;''', (classId,))
      classification = classification.fetchall()
      db.commit()
      return classification
    except sqlite3.Error as e:
      self.logger.logsqlite('getting classification for class', e)
    except Exception as e:
      self.logger.logunexpected('getting classification for class', e)
    db.commit()
    return []


  # Add mark
  def addStudentMark(self, mark: int, studentId: int, classificationId: int, comment: str=None):
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.execute('INSERT INTO studentMarks(mark, studentId, classificationId, comment) VALUES(?, ?, ?, ?);', (mark, studentId, classificationId, comment))
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a student mark', e, e.sqlite_errorcode, (mark, studentId, classificationId, comment))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a student mark', e)
    db.commit()
    return 0
  
  # Add marks for students marks: [mark, studentId, classificationId, comment (or None)]
  def addStudentMarks(self, marks: list):
    try:
      db = self.getDBConn()
      cursor = db.cursor()
      cursor.executemany('INSERT INTO studentMarks(mark, studentId, classificationId, comment) VALUES(?, ?, ?, ?);', marks)
    except sqlite3.Error as e:
      self.logger.logsqlite('adding a student mark', e, e.sqlite_errorcode, marks)
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('adding a student mark', e)
    db.commit()
    return 0


  # [id, mark, weight, title, comment, date, dayId, timeId]
  def getAllMarksForStudent(self, studentId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      marks = cursor.execute('''SELECT sm.id, sm.mark, c.weight, c.title, sm.comment, c.date, l.dayId, l.timeId FROM studentMarks as sm
                                    JOIN classification as c ON c.id=sm.classificationId
                                    JOIN schedules ON schedules.id=c.scheduleId
                                    JOIN lectures as l ON l.id=schedules.lectureId
                                    WHERE sm.studentId=?;''', (studentId,))
      marks = marks.fetchall()
      db.commit()
      return marks
    except sqlite3.Error as e:
      self.logger.logsqlite('getting marks for student', e)
    except Exception as e:
      self.logger.logunexpected('getting marks for student', e)
    db.commit()
    return []
  
  # [id, mark, comment, fname, lname, birthNumber]
  def getAllMarksForClassificaion(self, classificationId: int):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      marks = cursor.execute('''SELECT sm.id, sm.mark, sm.comment, n1.name, n2.name, p.birthNumber FROM studentMarks as sm
                                    JOIN people as p ON p.birthNumber=sm.studentId
                                    JOIN names as n1 ON n1.id=p.firstNameId
                                    JOIN names as n2 ON n2.id=p.lastNameId
                                    WHERE sm.classificationId=?;''', (classificationId,))
      marks = marks.fetchall()
      db.commit()
      return marks
    except sqlite3.Error as e:
      self.logger.logsqlite('getting marks for classification', e)
    except Exception as e:
      self.logger.logunexpected('getting marks for classification', e)
    db.commit()
    return []



  # Log in a user; returns id,role (if fail -> id = -1)
  def logInUser(self, username, password):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      # Get id, salt and password of a username
      account = cursor.execute('SELECT a.personId, a.password, a.disabled, roles.role FROM roles JOIN people ON roles.id=people.roleId JOIN accounts a ON people.id=a.personId WHERE a.username = ?;', (username,))
      account = account.fetchone()
      db.commit()
      # Check if the username exists
      if account:
        # Check if the account is disabled
        if account[2] == 1:
          return -1, ''
        # Check if the password is right
        if (checkpw(bytes(password, 'utf-8'), bytes(account[1]))):
          return account[0], account[3]
        else:
          self.logger.log(f'Password didn\'t match for user {username}', 2)
      else:
        self.logger.log(f'Unknown username: {username}', 2)
    except sqlite3.Error as e:
      self.logger.logsqlite('logging in a user', e, e.sqlite_errorcode, (username, password))
    except Exception as e:
      self.logger.logunexpected('logging in a user', e)
    db.commit()
    return -1, ''


  # return 0 if Username was found in table
  def checkIfUsernameExists(self, username):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      # If username is in accounts
      res1 = cursor.execute('SELECT * FROM accounts WHERE username = ?;', (username,))
      res1 = res1.fetchall()
      db.commit()
      if res1:
        return True
      return False
    except sqlite3.Error as e:
      self.logger.logsqlite('checking if a username already exists', e, e.sqlite_errorcode, (username))
    except Exception as e:
      self.logger.logunexpected('checking if a username already exists', e)
    db.commit()
    return True


  # Remove a user
  def removeUser(self, ix):
    try:
      
      db = self.getDBConn()
      cursor = db.cursor()
      # Find a user
      user = cursor.execute('SELECT username FROM accounts WHERE personId = ?;', (ix,))
      user = user.fetchone()
      if user:
        cursor.execute('DELETE FROM accounts WHERE personId = ?', (ix,))
      else:
        # If we were unable to find the id in accounts, we log it as a warning
        self.logger.log(f'Recieved remove request for id({ix}), however requested row is not present in accounts table aborting', 2)
    except sqlite3.Error as e:
      self.logger.logsqlite('removing a user', e, e.sqlite_errorcode, (ix))
      db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.logunexpected('removing a user', e)
    db.commit()
    return 0

  # initialize/DaysInWeek/Roles
  def initializeAll(self):
    self.initialize()
    self.initializeDaysInWeek()
    self.initializeRoles()
