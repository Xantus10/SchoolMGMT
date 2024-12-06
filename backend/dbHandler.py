import datetime
import sqlite3
from hashlib import sha256
from secrets import token_hex
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

    self.db = sqlite3.connect(self.dbLocation)
    self.db.execute('PRAGMA foreign_keys = ON;')


  # Hash a password, returns salt,hash tuple
  def hashPassword(self, password: str) -> tuple[str, str]:
    try:
      # Random salt
      salt = token_hex(32)
      # Hashed password with salt
      hashed = sha256(bytes.fromhex(salt) + bytes(password, 'utf-8')).hexdigest()
      return salt, hashed
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while hashing a password; Error message: {e}')
    return '', ''


  # Check provided password, salt with a hash, returns bool
  def checkHashedPassword(self, password: str, salt: str, checkHash: str) -> bool:
    try:
      return sha256(bytes.fromhex(salt) + bytes(password, 'utf-8')).hexdigest() == checkHash
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while checking a hashed password; Error message: {e}')
    return False


  # Initialize all database tables
  def initialize(self):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('CREATE TABLE IF NOT EXISTS buildings(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS classrooms(id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER NOT NULL, capacity INTEGER NOT NULL, buildingId INTEGER NOT NULL, CONSTRAINT FK_classrooms_buildingId FOREIGN KEY (buildingId) REFERENCES buildings(id), CONSTRAINT U_classrooms_number_buildingId UNIQUE (number, buildingId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS roles(id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS names(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT, birthNumber INTEGER NOT NULL UNIQUE, roleId INTEGER NOT NULL, firstNameId INTEGER NOT NULL, lastNameId INTEGER NOT NULL, CONSTRAINT FK_people_roleId FOREIGN KEY (roleId) REFERENCES roles(id), CONSTRAINT FK_people_firstNameId FOREIGN KEY (firstNameId) REFERENCES names(id), CONSTRAINT FK_people_lastNameId FOREIGN KEY (lastNameId) REFERENCES names(id));')
      cursor.execute('CREATE TABLE IF NOT EXISTS accounts(personId INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password TEXT NOT NULL, disabled INTEGER, CONSTRAINT FK_accounts_personId FOREIGN KEY (personId) REFERENCES people(id), CONSTRAINT CH_accounts_disabled CHECK (disabled IS NULL OR disabled=1));')
      cursor.execute('CREATE TABLE IF NOT EXISTS employees(personId INTEGER PRIMARY KEY, supervisorId INTEGER, CONSTRAINT FK_employees_personId FOREIGN KEY(personId) REFERENCES people(id), CONSTRAINT FK_employees_supervisorId FOREIGN KEY (supervisorId) REFERENCES employees(personId), CONSTRAINT CH_employees_supervisorId CHECK (supervisorId!=personId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS teachers(personId INTEGER PRIMARY KEY, strIdentifier TEXT NOT NULL UNIQUE, teachingFrom DATE NOT NULL, CONSTRAINT FK_teachers_personId FOREIGN KEY (personId) REFERENCES employees(personId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY AUTOINCREMENT, startYear INTEGER NOT NULL, groupNumber INTEGER, rootClassroomId INTEGER NOT NULL UNIQUE, courseId INTEGER NOT NULL, classTeacherId INTEGER NOT NULL, CONSTRAINT FK_classes_rootClassroomId FOREIGN KEY (rootClassroomId) REFERENCES classrooms(id), CONSTRAINT FK_classes_courseId FOREIGN KEY (courseId) REFERENCES courses(id), CONSTRAINT FK_classes_classTeacherId FOREIGN KEY (classTeacherId) REFERENCES teachers(personId), CONSTRAINT U_classes_startYear_courseId_groupNumber UNIQUE (startYear, courseId, groupNumber), CONSTRAINT CH_classes_groupNumber_startYear CHECK ((groupNumber=1 OR groupNumber=2 OR groupNumber IS NULL) AND (startYear>2000 AND startYear<=9999)));')
      cursor.execute('CREATE TABLE IF NOT EXISTS students(personId INTEGER PRIMARY KEY, classId INTEGER NOT NULL, half TEXT NOT NULL, CONSTRAINT FK_students_personId FOREIGN KEY (personId) REFERENCES people(id), CONSTRAINT FK_students_classId FOREIGN KEY (classId) REFERENCES classes(id), CONSTRAINT CH_students_half CHECK (half=\'A\' OR half=\'B\'));')
      cursor.execute('CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS teachersSubjectsExpertise(teacherId INTEGER, subjectId INTEGER, CONSTRAINT PK_teachersSubjectsExpertise PRIMARY KEY (teacherId, subjectId), CONSTRAINT FK_teachersSubjectsExpertise_teacherId FOREIGN KEY (teacherId) REFERENCES teachers(personId), CONSTRAINT FK_teachersSubjectsExpertise_subjectId FOREIGN KEY (subjectId) REFERENCES subjects(id));')
      cursor.execute('CREATE TABLE IF NOT EXISTS daysInWeek(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS lectureTimes(id INTEGER PRIMARY KEY, startTime TIME NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS lectures(id INTEGER PRIMARY KEY AUTOINCREMENT, isEvenWeek INTEGER NOT NULL, dayId INTEGER NOT NULL, timeId INTEGER NOT NULL, CONSTRAINT FK_lectures_dayId FOREIGN KEY (dayId) REFERENCES daysInWeek(id), CONSTRAINT FK_lectures_timeId FOREIGN KEY (timeId) REFERENCES lectureTimes(id), CONSTRAINT U_lectures_all UNIQUE (isEvenWeek, dayId, timeId), CONSTRAINT CH_lectures_isEvenWeek CHECK (isEvenWeek=0 OR isEvenWeek=1));')
      cursor.execute('CREATE TABLE IF NOT EXISTS schedules(id INTEGER PRIMARY KEY AUTOINCREMENT, lectureId INTEGER NOT NULL, classId INTEGER NOT NULL, teacherId INTEGER NOT NULL, subjectId INTEGER NOT NULL, fullOrAB TEXT NOT NULL, classroomId INTEGER NOT NULL, CONSTRAINT FK_schedules_lectureId FOREIGN KEY (lectureId) REFERENCES lectures(id), CONSTRAINT FK_schedules_classId FOREIGN KEY (classId) REFERENCES classes(id), CONSTRAINT FK_schedules_teachersubjectId FOREIGN KEY (teacherId, subjectId) REFERENCES teachersSubjectsExpertise(teacherId, subjectId), CONSTRAINT FK_schedules_classroomId FOREIGN KEY (classroomId) REFERENCES classrooms(id), CONSTRAINT U_schedules_lectureId_classId_fullOrAB UNIQUE(lectureId, classId, fullOrAB), CONSTRAINT U_schedules_lectureId_teacherId UNIQUE(lectureId, teacherId), CONSTRAINT U_schedules_lectureId_classroomId UNIQUE(lectureId, classroomId), CONSTRAINT CH_schedules_fullOrAB CHECK (fullOrAB=\'A\' OR fullOrAB=\'B\' OR fullOrAB=\'F\'));')
      cursor.execute('CREATE TABLE IF NOT EXISTS classification(id INTEGER PRIMARY KEY AUTOINCREMENT, weight REAL NOT NULL, date DATE NOT NULL, title TEXT NOT NULL, scheduleId INTEGER NOT NULL, CONSTRAINT FK_classification_scheduleId FOREIGN KEY (scheduleId) REFERENCES schedules(id), CONSTRAINT U_classification_scheduleId_date_title UNIQUE (scheduleId, date, title), CONSTRAINT CH_classification_weight CHECK (weight>0 AND weight<=1));')
      cursor.execute('CREATE TABLE IF NOT EXISTS studentMarks(id INTEGER PRIMARY KEY AUTOINCREMENT, mark REAL NOT NULL, studentId INTEGER NOT NULL, comment TEXT, classificationId INTEGER NOT NULL, CONSTRAINT FK_classification_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_classification_classificationId FOREIGN KEY (classificationId) REFERENCES classification(id), CONSTRAINT U_studentMarks_studentId_classificationId UNIQUE (studentId, classificationId), CONSTRAINT CH_studentMarks_mark CHECK (mark>=1 AND mark<=5 AND (mark%0.5)=0.0));')
      cursor.execute('CREATE TABLE IF NOT EXISTS studentComments(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE NOT NULL, studentId INTEGER NOT NULL, teacherId INTEGER NOT NULL, comment TEXT NOT NULL, CONSTRAINT FK_studentComments_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_studentComments_teacherId FOREIGN KEY (teacherId) REFERENCES teachers(personId));')
      cursor.execute('CREATE TABLE IF NOT EXISTS absenceTypes(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);')
      cursor.execute('CREATE TABLE IF NOT EXISTS studentsAbsence(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE NOT NULL, lectureId INTEGER NOT NULL, studentId INTEGER NOT NULL, absenceTypeId INTEGER NOT NULL, CONSTRAINT FK_studentsAbsence_lectureId FOREIGN KEY (lectureId) REFERENCES lectures(id), CONSTRAINT FK_studentsAbsence_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_studentsAbsence_absenceTypeId FOREIGN KEY (absenceTypeId) REFERENCES absenceTypes(id), CONSTRAINT U_studentsAbsence_date_lectureId_studentId UNIQUE (date, lectureId, studentId));')
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while initializing tables; Error message: {e}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while initializing tables; Error message: {e}')
    self.db.commit()
    return 0


  # Add a building with specified parameters
  def addBuilding(self, name: str, strIdentifier: str):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('INSERT INTO buildings(name, strIdentifier) VALUES(?, ?);', (name, strIdentifier))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a building; Error message: ({e.sqlite_errorcode}) {e}; Data: {(name, strIdentifier)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a building; Error message: {e}')
    self.db.commit()
    return 0

  def getAllBuildings(self) -> list[list[int, str, str]]:
    try:
      
      cursor = self.db.cursor()
      building = cursor.execute('SELECT * FROM buildings;')
      building = building.fetchall()
      self.db.commit()
      return building
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all buildings; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all buildings; Error message: {e}')
    self.db.commit()
    return []

  # [id, name, strID]
  def getBuildingByName(self, name: str) -> list[int, str, str]:
    try:
      
      cursor = self.db.cursor()
      building = cursor.execute('SELECT * FROM buildings WHERE name=?;', (name,))
      building = building.fetchone()
      self.db.commit()
      if building:
        return building
      self.logger.log(f'Building was not found for name {name}', 2)
      return []
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting a building; Error message: ({e.sqlite_errorcode}) {e}; Data: {(name)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting a building; Error message: {e}')
    self.db.commit()
    return []

  # [id, name, strID]
  def getBuildingById(self, buildingId: int) -> list[int, str, str]:
    try:
      
      cursor = self.db.cursor()
      building = cursor.execute('SELECT * FROM buildings WHERE id=?;', (buildingId,))
      building = building.fetchone()
      self.db.commit()
      if building:
        return building
      self.logger.log(f'Building was not found for id {buildingId}', 2)
      return []
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting a building; Error message: ({e.sqlite_errorcode}) {e}; Data: {(buildingId)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting a building; Error message: {e}')
    self.db.commit()
    return []



  def addClassroom(self, number: int, capacity: int, buildingId: int):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('INSERT INTO classrooms(number, capacity, buildingId) VALUES(?, ?, ?);', (number, capacity, buildingId))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a classroom; Error message: ({e.sqlite_errorcode}) {e}; Data: {(number, capacity, buildingId)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a classroom; Error message: {e}')
    self.db.commit()
    return 0

  # [id, number, capacity]
  def getAllClassroomsForBuilding(self, buildingId: int) -> list[list[int, int, int]]:
    try:
      
      cursor = self.db.cursor()
      classrooms = cursor.execute('SELECT * FROM classrooms WHERE buildingId=?;', (buildingId,))
      classrooms = classrooms.fetchall()
      self.db.commit()
      return classrooms
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all classrooms; Error message: ({e.sqlite_errorcode}) {e}; Data: {buildingId}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all classrooms; Error message: {e}')
    self.db.commit()
    return []

  def getClassroomId(self, number: int, buildingId: int) -> int:
    try:
      
      cursor = self.db.cursor()
      classrooms = cursor.execute('SELECT * FROM classrooms WHERE number=? AND buildingId=?;', (number, buildingId))
      classrooms = classrooms.fetchone()
      self.db.commit()
      return classrooms
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting classroomId; Error message: ({e.sqlite_errorcode}) {e}; Data: {(number, buildingId)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting classroomId; Error message: {e}')
    self.db.commit()
    return []



  def addCourse(self, name: str, strId: str):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('INSERT INTO courses(name, strIdentifier) VALUES(?, ?);', (name, strId))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a course; Error message: ({e.sqlite_errorcode}) {e}; Data: {(name, strId)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a course; Error message: {e}')
    self.db.commit()
    return 0

  def getAllCourses(self):
    try:
      
      cursor = self.db.cursor()
      courses = cursor.execute('SELECT * FROM courses;')
      courses = courses.fetchall()
      self.db.commit()
      return courses
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all courses; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all courses; Error message: {e}')
    self.db.commit()
    return []


  # Initialize basic roles (admin, teacher, student)
  def initializeRoles(self):
    try:
      
      cursor = self.db.cursor()
      default = [('admin',), ('teacher',), ('student',)]
      cursor.executemany('INSERT OR IGNORE INTO roles(role) VALUES(?);', default)
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a role; Error message: ({e.sqlite_errorcode}) {e}; Data: {(default)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a role; Error message: {e}')
    self.db.commit()
    return 0

  def addRole(self, role: str):
    try:
      
      cursor = self.db.cursor()
      role = role.lower()
      cursor.execute('INSERT INTO roles(role) VALUES(?);', (role,))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a role; Error message: ({e.sqlite_errorcode}) {e}; Data: {(role)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a role; Error message: {e}')
    self.db.commit()
    return 0

  def getAllRoles(self):
    try:
      
      cursor = self.db.cursor()
      roles = cursor.execute('SELECT * FROM roles;')
      roles = roles.fetchall()
      self.db.commit()
      return roles
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all roles; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all roles; Error message: {e}')
    self.db.commit()
    return []



  def addPerson(self, birthNumber: int, roleId: int, firstName: str, lastName: str):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('INSERT OR IGNORE INTO names(name) VALUES(?)', (firstName,))
      cursor.execute('INSERT OR IGNORE INTO names(name) VALUES(?)', (lastName,))
      fnId = cursor.execute('SELECT id FROM names WHERE name=?', (firstName,))
      fnId = fnId.fetchone()[0]
      lnId = cursor.execute('SELECT id FROM names WHERE name=?', (lastName,))
      lnId = lnId.fetchone()[0]
      cursor.execute('INSERT INTO people(birthNumber, roleId, firstNameId, lastNameId) VALUES(?, ?, ?, ?)', (birthNumber, roleId, fnId, lnId))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a person; Error message: ({e.sqlite_errorcode}) {e}; Data: {(birthNumber, roleId, firstName, lastName)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a person; Error message: {e}')
    self.db.commit()
    return 0

  # [id, role, fname, lname]
  def getPersonByBirthNumber(self, birthNumber: int) -> list[int, str, str, str]:
    try:
      
      cursor = self.db.cursor()
      person = cursor.execute('''SELECT people.id, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE people.birthNumber=?;''', (birthNumber,))
      person = person.fetchone()
      self.db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting person(bn); Error message: ({e.sqlite_errorcode}) {e}; Data: {birthNumber}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting person(bn); Error message: {e}')
    self.db.commit()
    return []

  # [birthNumber, role, fname, lname]
  def getPersonById(self, pid: int) -> list[int, str, str, str]:
    try:
      
      cursor = self.db.cursor()
      person = cursor.execute('''SELECT people.birthNumber, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE people.id=?;''', (pid,))
      person = person.fetchone()
      self.db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting person(id); Error message: ({e.sqlite_errorcode}) {e}; Data: {pid}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting person(id); Error message: {e}')
    self.db.commit()
    return []

  # [id, birthNumber, role, fname, lname]
  def getAllPeopleWithName(self, firstName: str='', lastName: str='') -> list[list[int, int, str, str, str]]:
    try:
      if not firstName and not lastName: return []
      
      cursor = self.db.cursor()
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
      self.db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all people by role; Error message: ({e.sqlite_errorcode}) {e}; Data: {firstName, lastName}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all people by name; Error message: {e}')
    self.db.commit()
    return []

  # [id, birthNumber, fname, lname]
  def getAllPeopleWithRole(self, role: str) -> list[list[int, int, str, str]]:
    try:
      
      cursor = self.db.cursor()
      person = cursor.execute('''SELECT people.id, people.birthNumber, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  WHERE roles.role=?;''', (role,))
      person = person.fetchall()
      self.db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all people by role; Error message: ({e.sqlite_errorcode}) {e}; Data: {role}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all people by role; Error message: {e}')
    self.db.commit()
    return []


  def addAccount(self, personId: int, username: str, password: str):
    try:
      
      cursor = self.db.cursor()
      # Hash the password
      salt, hashed = self.hashPassword(password)
      # Data for INSERT
      data = (personId, username, salt, hashed)
      # INSERT into accounts table
      cursor.execute('INSERT INTO accounts(personId, username, salt, password) VALUES(?, ?, ?, ?);', data)
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a user; Error message: ({e.sqlite_errorcode}) {e}; Data: {(personId, username, salt, password)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a user; Error message: {e}')
    self.db.commit()
    return 0

  def getAccountInfoById(self, personId: int) -> list[str, bool]:
    try:
      
      cursor = self.db.cursor()
      account = cursor.execute('SELECT username, disabled FROM accounts WHERE personId=?;', (personId,))
      account = list(account.fetchone())
      self.db.commit()
      if account: account[1] = bool(account[1])
      return account
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting account; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting account; Error message: {e}')
    self.db.commit()
    return []


  # Check if inserting the row with specified pid and sid will cause a loop where pid is super of sid and sid is super of pid
  def checkForSupervisorLoop(self, personId: int, supervisorId: int) -> bool:
    try:
        
        cursor = self.db.cursor()
        # Get supervisor
        sup = cursor.execute('SELECT * FROM employees WHERE personId=?', (supervisorId,))
        sup = sup.fetchone()
        self.db.commit()
        if sup: return sup[1] == personId
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while checking supervisor loops; Error message: ({e.sqlite_errorcode}) {e}; Data: {(personId, supervisorId)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while checking supervisor loops; Error message: {e}')
    self.db.commit()
    return 0

  def addEmployee(self, personId: int, supervisorId: int=None):
    try:
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO employees(personId, supervisorId) VALUES(?, ?);', (personId, supervisorId))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding an employee; Error message: ({e.sqlite_errorcode}) {e}; Data: {(personId, supervisorId)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding an employee; Error message: {e}')
    self.db.commit()
    return 0

  def getEmployeeById(self, personId: int) -> list[int, int]:
    try:
      
      cursor = self.db.cursor()
      emp = cursor.execute('SELECT * FROM employees WHERE;')
      emp = emp.fetchall()
      self.db.commit()
      return emp
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting employee; Error message: ({e.sqlite_errorcode}) {e}; Data: {personId};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting employee; Error message: {e}')
    self.db.commit()
    return []

  # [id, role, fname, lname]
  def getAllEmployeesWithSupervisor(self, supervisorId: int) -> list[int, str, str, str]:
    try:
      
      cursor = self.db.cursor()
      person = cursor.execute('''SELECT people.id, roles.role, fn.name, ln.name FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  JOIN employees ON employees.personId=people.id
                                                  WHERE employees.supervisorId=?;''', (supervisorId,))
      person = person.fetchall()
      self.db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all employees by supervisor; Error message: ({e.sqlite_errorcode}) {e}; Data: {supervisorId}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all employees by supervisor; Error message: {e}')
    self.db.commit()
    return []

  def getAllEmployeesWithName(self, firstName: str='', lastName: str='') -> list[list[int, int, str, str, str]]:
    try:
      if not firstName and not lastName: return []
      
      cursor = self.db.cursor()
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
      self.db.commit()
      return person
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all employees by name; Error message: ({e.sqlite_errorcode}) {e}; Data: {firstName, lastName}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all employees by name; Error message: {e}')
    self.db.commit()
    return []


  def addTeacher(self, personId: int, teachingFrom: datetime.date, strIdentifier: str):
    try:
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO teachers(personId, teachingFrom, strIdentifier) VALUES(?, ?, ?);', (personId, teachingFrom, strIdentifier))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a teacher; Error message: ({e.sqlite_errorcode}) {e}; Data: {(personId, teachingFrom, strIdentifier)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a teacher; Error message: {e}')
    self.db.commit()
    return 0

  # [id, fname, lname, strID, teachFrom]
  def getAllTeachers(self) -> list[int, str, str, str, datetime.datetime]:
    try:
      
      cursor = self.db.cursor()
      teachers = cursor.execute('''SELECT people.id, fn.name, ln.name, teachers.strIdentifier, teachers.teachingFrom FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN roles ON roles.id=people.roleId
                                                  JOIN teachers ON teachers.personId=people.id;''')
      teachers = teachers.fetchall()
      self.db.commit()
      for i, teacher in enumerate(teachers):
        teachers[i] = list(teacher)
        teachers[i][-1] = datetime.datetime.strptime(teachers[i][-1], '%Y-%m-%d')
      return teachers
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all teachers; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all teachers; Error message: {e}')
    self.db.commit()
    return []

  # [id, fname, lname, teachFrom]
  def getTeacherByStrId(self, strId: str) -> list[int, str, str, datetime.datetime]:
    try:
      
      cursor = self.db.cursor()
      teachers = cursor.execute('''SELECT people.id, fn.name, ln.name, teachers.teachingFrom FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN teachers ON teachers.personId=people.id
                                                  WHERE teachers.strIdentifier=?;''', (strId,))
      teachers = teachers.fetchone()
      self.db.commit()
      return teachers
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting a teacher; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting a teacher; Error message: {e}')
    self.db.commit()
    return []


  def addClass(self, courseId: int, startYear: int, rootClassroomId: int, classTeacherId: int, groupNumber: int=None):
    try:
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO classes(startYear, rootClassroomId, courseId, classTeacherId, groupNumber) VALUES(?, ?, ?, ?, ?);', (startYear, rootClassroomId, courseId, classTeacherId, groupNumber))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a class; Error message: ({e.sqlite_errorcode}) {e}; Data: {(startYear, rootClassroomId, courseId, classTeacherId, groupNumber)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a class; Error message: {e}')
    self.db.commit()
    return 0

  # [id, courseStrID, startYear, groupNumber, classTeacherId, rootClassroomId]
  def getAllClasses(self) -> list[int, str, int, int, int, int]:
    try:
      
      cursor = self.db.cursor()
      classes = cursor.execute('''SELECT classes.id, courses.strIdentifier, classes.startYear, classes.groupNumber, classes.classTeacherId, classes.rootClassroomId FROM classes
                                                  JOIN courses ON courses.id=classes.courseId;''')
      classes = classes.fetchall()
      self.db.commit()
      return classes
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all classes; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all classes; Error message: {e}')
    self.db.commit()
    return []

  # [id, courseStrID, startYear, groupNumber, rootClassroomId]
  def getAllClassesWithTeacher(self, classTeacherId: int) -> list[int, str, int, int, int]:
    try:
      
      cursor = self.db.cursor()
      classes = cursor.execute('''SELECT classes.id, courses.strIdentifier, classes.startYear, classes.groupNumber, classes.rootClassroomId FROM classes
                                                  JOIN courses ON courses.id=classes.courseId
                                                  WHERE classes.classTeacherId=?;''', (classTeacherId,))
      classes = classes.fetchall()
      self.db.commit()
      return classes
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all classes; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all classes; Error message: {e}')
    self.db.commit()
    return []



  def addStudent(self, personId: int, classId: int, half: str):
    try:
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO students(personId, classId, half) VALUES(?, ?, ?);', (personId, classId, half))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a student; Error message: ({e.sqlite_errorcode}) {e}; Data: {(personId, classId, half)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a student; Error message: {e}')
    self.db.commit()
    return 0

  # [id, fname, lname, half]
  def getAllStudentsWithClassHalf(self, classId: int, half: str=None) -> list[int, str, str, str]:
    try:
      
      cursor = self.db.cursor()
      data = (classId, half) if half else (classId,)
      students = cursor.execute(f'''SELECT people.id, fn.name, ln.name, students.half FROM people
                                                  JOIN names fn ON fn.id=people.firstNameId
                                                  JOIN names ln ON ln.id=people.lastNameId
                                                  JOIN students ON students.personId=people.id
                                                  WHERE students.classId=?{" AND students.half=?" if half else ""};''', data)
      students = students.fetchall()
      self.db.commit()
      return students
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all students; Error message: ({e.sqlite_errorcode}) {e}; Data: {(classId, half)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all students; Error message: {e}')
    self.db.commit()
    return []



  def addSubject(self, name: str, strIdentifier: str):
    try:
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO subjects(name, strIdentifier) VALUES(?, ?);', (name, strIdentifier))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a subject; Error message: ({e.sqlite_errorcode}) {e}; Data: {(name, strIdentifier)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a subject; Error message: {e}')
    self.db.commit()
    return 0

  # [id, name, strID]
  def getAllSubjects(self) -> list[int, str, str]:
    try:
      
      cursor = self.db.cursor()
      subjects = cursor.execute('SELECT * FROM subjects;')
      subjects = subjects.fetchall()
      self.db.commit()
      return subjects
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all subjects; Error message: ({e.sqlite_errorcode}) {e};')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all subjects; Error message: {e}')
    self.db.commit()
    return []



  def addTeacherSubjectExpertise(self, teacherId: int, subjectId: int):
    try:
        
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO teachersSubjectsExpertise(teacherId, subjectId) VALUES(?, ?);', (teacherId, subjectId))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding a teacher subject; Error message: ({e.sqlite_errorcode}) {e}; Data: {(teacherId, subjectId)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding a teacher subject; Error message: {e}')
    self.db.commit()
    return 0

  # [id, strID]
  def getAllExpertiseWithTeacher(self, teacherId: int) -> list[int, str]:
    try:
      
      cursor = self.db.cursor()
      expertise = cursor.execute('''SELECT subjects.id, subjects.strIdentifier FROM teachersSubjectsExpertise
                                                  JOIN subjects ON teachersSubjectsExpertise.subjectId=subjects.id
                                                  WHERE teachersSubjectsExpertise.teacherId=?''', (teacherId,))
      expertise = expertise.fetchall()
      self.db.commit()
      return expertise
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all expertise(t); Error message: ({e.sqlite_errorcode}) {e}; Data: {(teacherId)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all expertise(t); Error message: {e}')
    self.db.commit()
    return []

  # [id, strID]
  def getAllExpertiseWithSubject(self, subjectId: int) -> list[int, str]:
    try:
      
      cursor = self.db.cursor()
      expertise = cursor.execute('''SELECT teachers.personId, teachers.strIdentifier FROM teachersSubjectsExpertise
                                                  JOIN teachers ON teachers.personId=teachersSubjectsExpertise.teacherId
                                                  WHERE teachersSubjectsExpertise.subjectId=?;''', (subjectId,))
      expertise = expertise.fetchall()
      self.db.commit()
      return expertise
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all expertise(s); Error message: ({e.sqlite_errorcode}) {e}; Data: {(subjectId)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all expertise(s); Error message: {e}')
    self.db.commit()
    return []



  def initializeDaysInWeek(self):
    try:
      
      cursor = self.db.cursor()
      days = [(1,'Monday'), (2,'Tuesday'), (3,'Wednesday'), (4,'Thursday'), (5,'Friday'), (6,'Saturday'), (7,'Sunday')]
      cursor.executemany('INSERT OR IGNORE INTO daysInWeek(id, name) VALUES(?, ?)', days)
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while initializing daysInWeek; Error message: ({e.sqlite_errorcode}) {e};')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while initializing daysInWeek; Error message: {e}')
    self.db.commit()
    return 0


  def addLectureTime(self, lectureId: int, time: datetime.datetime):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('INSERT INTO lectureTimes(id, startTime) VALUES(?, ?)', (lectureId, time))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding lectureTime; Error message: ({e.sqlite_errorcode}) {e};')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding lectureTime; Error message: {e}')
    self.db.commit()
    return 0


  def initializeLectures(self):
    try:
      
      cursor = self.db.cursor()
      days = cursor.execute('SELECT id FROM daysInWeek')
      days = days.fetchall()
      times = cursor.execute('SELECT id FROM lectureTimes')
      times = times.fetchall()
      for i in range(len(days)):
        days[i] = days[i][0]
      for i in range(len(times)):
        times[i] = times[i][0]
      cursor.executemany('INSERT OR IGNORE INTO lectures(isEvenWeek, dayId, timeId) VALUES(?, ?, ?)', list(product([0,1], days, times)))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while initializing lectures; Error message: ({e.sqlite_errorcode}) {e};')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while initializing lectures; Error message: {e}')
    self.db.commit()
    return 0

  # [id, day, time, isevenweek]
  def getAllLectures(self) -> list[int, str, datetime.datetime, bool]:
    try:
      
      cursor = self.db.cursor()
      lectures = cursor.execute('''SELECT lectures.id, d.name, t.id, t.startTime, lectures.isEvenWeek FROM lectures
                                                  JOIN daysInWeek d ON lectures.dayId=d.id
                                                  JOIN lectureTimes t ON lectures.timeId=t.id;''')
      lectures = lectures.fetchall()
      self.db.commit()
      for i, lecture in enumerate(lectures):
        lectures[i] = list(lecture)
        lectures[i][3] = datetime.datetime.strptime(lectures[i][3], '%Y-%m-%d %H:%M:%S')
        lectures[i][4] = bool(lectures[i][4])
      return lectures
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting all lectures; Error message: {e}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting all lectures; Error message: {e}')
    self.db.commit()
    return []



  def addScheduleSingle(self, lectureId: int, classId: int, teacherId: int, subjectId: int, classroomId: int, FullORAB: str):
    try:
      
      cursor = self.db.cursor()
      cursor.execute('INSERT INTO schedules(lectureId, classId, teacherId, subjectId, classroomId, FullORAB) VALUES(?, ?, ?, ?, ?, ?)', (lectureId, classId, teacherId, subjectId, classroomId, FullORAB))
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while adding schedule single; Error message: ({e.sqlite_errorcode}) {e};')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while adding schedule single; Error message: {e}')
    self.db.commit()
    return 0

  # [lectureId, day, timeId, time, evenWeek, teacherStrID, subjectStrID, buildingStrID, classroomNum, fullOrAB]
  def getScheduleForClass(self, classId: int):
    try:
      
      cursor = self.db.cursor()
      schedule = cursor.execute('''SELECT lectures.id, d.name, t.id, t.startTime, lectures.isEvenWeek, teachers.strIdentifier, subjects.strIdentifier, buildings.strIdentifier, classrooms.number, schedules.fullOrAB FROM schedules
                                                  JOIN lectures ON schedules.lectureId=lectures.id
                                                  JOIN daysInWeek d ON lectures.dayId=d.id
                                                  JOIN lectureTimes t ON lectures.timeId=t.id
                                                  JOIN teachers ON schedules.teacherId=teachers.personId
                                                  JOIN subjects ON schedules.subjectId=subjects.id
                                                  JOIN classrooms ON schedules.classroomId=classrooms.id
                                                  JOIN buildings ON classrooms.buildingId=buildings.id
                                                  WHERE schedules.classId=?;''', (classId,))
      schedule = schedule.fetchall()
      self.db.commit()
      for i, lecture in enumerate(schedule):
        schedule[i] = list(lecture)
        schedule[i][3] = datetime.datetime.strptime(schedule[i][3], '%Y-%m-%d %H:%M:%S')
        schedule[i][4] = bool(schedule[i][4])
      return schedule
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting schedule for class; Error message: {e}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting schedule for class; Error message: {e}')
    self.db.commit()
    return []

  # [lectureId, day, timeId, time, evenWeek, courseStrID, classStratYear, classGroupNumber, subjectStrID, buildingStrID, classroomNum, fullOrAB]
  def getScheduleForTeacher(self, teacherId: int):
    try:
      
      cursor = self.db.cursor()
      schedule = cursor.execute('''SELECT lectures.id, d.name, t.id, t.startTime, lectures.isEvenWeek, courses.strIdentifier, classes.startYear, classes.groupNumber, subjects.strIdentifier, buildings.strIdentifier, classrooms.number, schedules.fullOrAB FROM schedules
                                                  JOIN lectures ON schedules.lectureId=lectures.id
                                                  JOIN daysInWeek d ON lectures.dayId=d.id
                                                  JOIN lectureTimes t ON lectures.timeId=t.id
                                                  JOIN classes ON schedules.classId=classes.id
                                                  JOIN courses ON classes.courseId=courses.id
                                                  JOIN subjects ON schedules.subjectId=subjects.id
                                                  JOIN classrooms ON schedules.classroomId=classrooms.id
                                                  JOIN buildings ON classrooms.buildingId=buildings.id
                                                  WHERE schedules.teacherId=?;''', (teacherId,))
      schedule = schedule.fetchall()
      self.db.commit()
      for i, lecture in enumerate(schedule):
        schedule[i] = list(lecture)
        schedule[i][3] = datetime.datetime.strptime(schedule[i][3], '%Y-%m-%d %H:%M:%S')
        schedule[i][4] = bool(schedule[i][4])
      return schedule
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting schedule for class; Error message: {e}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting schedule for class; Error message: {e}')
    self.db.commit()
    return []

  # [lectureId, day, timeId, time, evenWeek, courseStrID, classStratYear, classGroupNumber, subjectStrID, teacherStrID, fullOrAB]
  def getScheduleForClassroom(self, classroomId: int):
    try:
      
      cursor = self.db.cursor()
      schedule = cursor.execute('''SELECT lectures.id, d.name, t.id, t.startTime, lectures.isEvenWeek, courses.strIdentifier, classes.startYear, classes.groupNumber, subjects.strIdentifier, teachers.strIdentifier, schedules.fullOrAB FROM schedules
                                                  JOIN lectures ON schedules.lectureId=lectures.id
                                                  JOIN daysInWeek d ON lectures.dayId=d.id
                                                  JOIN lectureTimes t ON lectures.timeId=t.id
                                                  JOIN classes ON schedules.classId=classes.id
                                                  JOIN courses ON classes.courseId=courses.id
                                                  JOIN subjects ON schedules.subjectId=subjects.id
                                                  JOIN teachers ON schedules.teacherId=teachers.personId
                                                  WHERE schedules.classroomId=?;''', (classroomId,))
      schedule = schedule.fetchall()
      self.db.commit()
      for i, lecture in enumerate(schedule):
        schedule[i] = list(lecture)
        schedule[i][3] = datetime.datetime.strptime(schedule[i][3], '%Y-%m-%d %H:%M:%S')
        schedule[i][4] = bool(schedule[i][4])
      return schedule
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while getting schedule for class; Error message: {e}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while getting schedule for class; Error message: {e}')
    self.db.commit()
    return []









  # Log in a user; returns id,role (if fail -> id = -1)
  def logInUser(self, username, password):
    try:
      
      cursor = self.db.cursor()
      # Get id, salt and password of a username
      account = cursor.execute('SELECT a.personId, a.salt, a.password, a.disabled, roles.role FROM roles JOIN people ON roles.id=people.roleId JOIN accounts a ON people.id=a.personId WHERE a.username = ?;', (username,))
      account = account.fetchone()
      self.db.commit()
      # Check if the username exists
      if account:
        # Check if the account is disabled
        if account[3] == 1:
          return -1, ''
        # Check if the password is right
        if (self.checkHashedPassword(password, account[1], account[2])):
          return account[0], account[4]
        else:
          self.logger.log(f'Password didn\'t match for user {username}', 2)
      else:
        self.logger.log(f'Unknown username: {username}', 2)
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while logging in a user; Error message: ({e.sqlite_errorcode}) {e}; Data: {(username, password)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while logging in a user; Error message: {e}')
    self.db.commit()
    return -1, ''


  # return 0 if Username was found in table
  def checkIfUsernameExists(self, username):
    try:
      
      cursor = self.db.cursor()
      # If username is in accounts
      res1 = cursor.execute('SELECT * FROM accounts WHERE username = ?;', (username,))
      res1 = res1.fetchall()
      self.db.commit()
      if res1:
        return True
      return False
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while checking if a username already exists; Error message: ({e.sqlite_errorcode}) {e}; Data: {(username)}')
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while checking if a username already exists; Error message: {e}')
    self.db.commit()
    return True


  # Remove a user
  def removeUser(self, ix):
    try:
      
      cursor = self.db.cursor()
      # Find a user
      user = cursor.execute('SELECT username FROM accounts WHERE personId = ?;', (ix,))
      user = user.fetchone()
      if user:
        cursor.execute('DELETE FROM accounts WHERE personId = ?', (ix,))
      else:
        # If we were unable to find the id in accounts, we log it as a warning
        self.logger.log(f'Recieved remove request for id({ix}), however requested row is not present in accounts table aborting', 2)
    except sqlite3.Error as e:
      self.logger.log(f'An error in SQL syntax occurred while removing a user; Error message: ({e.sqlite_errorcode}) {e}; Data: {(ix)}')
      self.db.commit()
      return e.sqlite_errorcode
    except Exception as e:
      self.logger.log(f'An unexpected error occurred while removing a user; Error message: {e}')
    self.db.commit()
    return 0

  # initialize/DaysInWeek/Roles
  def initializeAll(self):
    self.initialize()
    self.initializeDaysInWeek()
    self.initializeRoles()
