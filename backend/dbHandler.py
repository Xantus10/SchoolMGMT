import sqlite3
from hashlib import sha256
from secrets import token_hex

from logs import Logger
logger = Logger()


dbLocation = 'data/database.db'


# Hash a password, returns salt,hash tuple
def hashPassword(password: str) -> tuple[str, str]:
  try:
    # Random salt
    salt = token_hex(32)
    # Hashed password with salt
    hashed = sha256(bytes.fromhex(salt) + bytes(password, 'utf-8')).hexdigest()
    return salt, hashed
  except Exception as e:
    logger.log(f'An unexpected error occurred while hashing a password; Error message: {e}')
  return '', ''


# Check provided password, salt with a hash, returns bool
def checkHashedPassword(password: str, salt: str, checkHash: str) -> bool:
  try:
    return sha256(bytes.fromhex(salt) + bytes(password, 'utf-8')).hexdigest() == checkHash
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking a hashed password; Error message: {e}')
  return False


# Initialize all database tables
def initialize():
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS buildings(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier  NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS classrooms(id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER NOT NULL, capacity INTEGER NOT NULL, buildingId INTEGER NOT NULL, CONSTRAINT FK_classrooms_buildingId FOREIGN KEY (buildingId) REFERENCES buildings(id), CONSTRAINT U_classrooms_number_buildingId UNIQUE (number, buildingId));')
    cursor.execute('CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS roles(id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS names(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT, birthNumber INTEGER NOT NULL UNIQUE, roleId INTEGER NOT NULL, firstNameId INTEGER NOT NULL, lastNameId INTEGER NOT NULL, CONSTRAINT FK_people_roleId FOREIGN KEY (roleId) REFERENCES roles(id), CONSTRAINT FK_people_firstNameId FOREIGN KEY (firstNameId) REFERENCES names(id), CONSTRAINT FK_people_lastNameId FOREIGN KEY (lastNameId) REFERENCES names(id));')
    cursor.execute('CREATE TABLE IF NOT EXISTS accounts(personId INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password TEXT NOT NULL, disabled INTEGER, CONSTRAINT FK_accounts_personId FOREIGN KEY (personId) REFERENCES people(id), CONSTRAINT CH_accounts_disabled CHECK (disabled IS NULL OR disabled=1));')
    cursor.execute('CREATE TABLE IF NOT EXISTS employees(personId INTEGER PRIMARY KEY, supervisorId INTEGER, CONSTRAINT FK_employees_personId FOREIGN KEY(personId) REFERENCES people(id), CONSTRAINT FK_employees_supervisorId FOREIGN KEY (supervisorId) REFERENCES employees(id), CONSTRAINT CH_employees_supervisorId CHECK (supervisorId!=personId));')
    cursor.execute('CREATE TABLE IF NOT EXISTS teachers(personId INTEGER EGER PRIMARY KEY, strIdentifier TEXT NOT NULL UNIQUE, teachingFrom DATE NOT NULL, CONSTRAINT FK_teachers_personId FOREIGN KEY(personId) REFERENCES employees(personId));')
    cursor.execute('CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY AUTOINCREMENT, startDate DATE NOT NULL, groupNumber INTEGER, rootClassroomId INTEGER NOT NULL UNIQUE, courseId INTEGER NOT NULL, classTeacherId INTEGER NOT NULL, CONSTRAINT FK_classes_rootClassroomId FOREIGN KEY (rootClassroomId) REFERENCES classrooms(id), CONSTRAINT FK_classes_courseId FOREIGN KEY (courseId) REFERENCES courses(id), CONSTRAINT FK_classes_classTeacherId FOREIGN KEY (classTeacherId) REFERENCES teachers(personId), CONSTRAINT U_classes_startDate_courseId_groupNumber UNIQUE (startDate, courseId, groupNumber), CONSTRAINT CH_classes_groupNumber CHECK (groupNumber=1 OR groupNumber=2 OR groupNumber IS NULL));')
    cursor.execute('CREATE TABLE IF NOT EXISTS students(personId INTEGER PRIMARY KEY, classId INTEGER NOT NULL, half TEXT NOT NULL, CONSTRAINT FK_students_personId FOREIGN KEY(personId) REFERENCES people(personId), CONSTRAINT FK_students_classId FOREIGN KEY (classId) REFERENCES classes(id), CONSTRAINT CH_students_half CHECK (half=\'A\' OR half=\'B\'));')
    cursor.execute('CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, strIdentifier TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS teachersSubjectsExpertise(teacherId INTEGER, subjectId INTEGER, CONSTRAINT PK_teachersSubjectsExpertise PRIMARY KEY (teacherId, subjectId), CONSTRAINT FK_teachersSubjectsExpertise_teacherId FOREIGN KEY (teacherId) REFERENCES teachers(personId), CONSTRAINT FK_teachersSubjectsExpertise_subjectId FOREIGN KEY (subjectId) REFERENCES subjects(id));')
    cursor.execute('CREATE TABLE IF NOT EXISTS daysInWeek(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS lectureTimes(id INTEGER PRIMARY KEY, startTime TIME NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS lectures(id INTEGER PRIMARY KEY AUTOINCREMENT, isEvenWeek INTEGER NOT NULL, dayId INTEGER NOT NULL, timeId INTEGER NOT NULL, CONSTRAINT FK_lectures_dayId FOREIGN KEY (dayId) REFERENCES daysInWeek(id), CONSTRAINT FK_lectures_timeId FOREIGN KEY (timeId) REFERENCES lectureTimes(id), CONSTRAINT U_lectures_all UNIQUE (isEvenWeek, dayId, timeId), CONSTRAINT CH_lectures_isEvenWeek CHECK (isEvenWeek=0 OR isEvenWeek=1));')
    cursor.execute('CREATE TABLE IF NOT EXISTS schedules(id INTEGER PRIMARY KEY AUTOINCREMENT, lectureId INTEGER NOT NULL, classId INTEGER NOT NULL, teacherId INTEGER NOT NULL, subjectId INTEGER NOT NULL, fullOrAB TEXT NOT NULL, classroomId INTEGER NOT NULL, CONSTRAINT FK_schedules_lectureId FOREIGN KEY (lectureId) REFERENCES lectures(id), CONSTRAINT FK_schedules_classId FOREIGN KEY (classId) REFERENCES classes(id), CONSTRAINT FK_schedules_teacherId FOREIGN KEY (teacherId) REFERENCES teachersSubjectsExpertise(teacherId), CONSTRAINT FK_schedules_subjectId FOREIGN KEY (subjectId) REFERENCES teachersSubjectsExpertise(subjectId), CONSTRAINT FK_schedules_classroomId FOREIGN KEY (classroomId) REFERENCES classrooms(id), CONSTRAINT U_schedules_lectureId_classId_fullOrAB UNIQUE(lectureId, classId, fullOrAB), CONSTRAINT U_schedules_lectureId_teacherId UNIQUE(lectureId, teacherId), CONSTRAINT U_schedules_lectureId_classroomId UNIQUE(lectureId, classroomId), CONSTRAINT CH_schedules_fullOrAB CHECK (fullOrAB=\'A\' OR fullOrAB=\'B\' OR fullOrAB=\'F\'));')
    cursor.execute('CREATE TABLE IF NOT EXISTS marksTitles(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS classification(id INTEGER PRIMARY KEY AUTOINCREMENT, mark REAL NOT NULL, weight INTEGER NOT NULL, teacherId INTEGER NOT NULL, subjectId INTEGER NOT NULL, studentId INTEGER NOT NULL, date DATE NOT NULL, titleId INTEGER NOT NULL, comment TEXT, CONSTRAINT FK_classification_teacherId FOREIGN KEY (teacherId) REFERENCES teachersSubjectsExpertise(teacherId), CONSTRAINT FK_classification_subjectId FOREIGN KEY (subjectId) REFERENCES teachersSubjectsExpertise(subjectId), CONSTRAINT FK_classification_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_classification_titleId FOREIGN KEY (titleId) REFERENCES marksTitles(id), CONSTRAINT U_classification_studentId_date_titleId UNIQUE (studentId, date, titleId), CONSTRAINT CH_classification_mark_weight CHECK (mark>=1 AND mark<=5 AND (mark%0.5)=0.0 AND weight>=1 AND weight<=10));')
    cursor.execute('CREATE TABLE IF NOT EXISTS studentComments(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE NOT NULL, studentId INTEGER NOT NULL, teacherId INTEGER NOT NULL, comment TEXT NOT NULL, CONSTRAINT FK_studentComments_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_studentComments_teacherId FOREIGN KEY (teacherId) REFERENCES teachers(personId));')
    cursor.execute('CREATE TABLE IF NOT EXISTS absenceTypes(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);')
    cursor.execute('CREATE TABLE IF NOT EXISTS studentsAbsence(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE NOT NULL, lectureId INTEGER NOT NULL, studentId INTEGER NOT NULL, absenceTypeId INTEGER NOT NULL, CONSTRAINT FK_studentsAbsence_lectureId FOREIGN KEY (lectureId) REFERENCES lectures(id), CONSTRAINT FK_studentsAbsence_studentId FOREIGN KEY (studentId) REFERENCES students(personId), CONSTRAINT FK_studentsAbsence_absenceTypeId FOREIGN KEY (absenceTypeId) REFERENCES absenceTypes(id), CONSTRAINT U_studentsAbsence_date_lectureId_studentId UNIQUE (date, lectureId, studentId));')
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while initializing tables; Error message: {e}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while initializing tables; Error message: {e}')
  db.commit()
  return True


# Add a building with specified parameters
def addBuilding(name: str, strIdentifier: str):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    cursor.execute('INSERT INTO buildings(name, strIdentifier) VALUES(?, ?);', (name, strIdentifier))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a building; Error message: {e}; Data: {(name, strIdentifier)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a building; Error message: {e}')
  db.commit()
  return True

def getAllBuildings() -> list[list[int, str, str]]:
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    building = cursor.execute('SELECT * FROM buildings;')
    building = building.fetchall()
    db.commit()
    return building
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting all buildings; Error message: {e};')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting all buildings; Error message: {e}')
  db.commit()
  return []

# [id, name, strID]
def getBuildingByName(name: str) -> list[int, str, str]:
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    building = cursor.execute('SELECT * FROM buildings WHERE name=?;', (name,))
    building = building.fetchone()
    db.commit()
    if building:
      return building
    logger.log(f'Building was not found for name {name}', 2)
    return []
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting a building; Error message: {e}; Data: {(name)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting a building; Error message: {e}')
  db.commit()
  return []

# [id, name, strID]
def getBuildingById(buildingId: int) -> list[int, str, str]:
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    building = cursor.execute('SELECT * FROM buildings WHERE id=?;', (buildingId,))
    building = building.fetchone()
    db.commit()
    if building:
      return building
    logger.log(f'Building was not found for id {buildingId}', 2)
    return []
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting a building; Error message: {e}; Data: {(buildingId)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting a building; Error message: {e}')
  db.commit()
  return []



def addClassroom(number: int, capacity: int, buildingId: int):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    cursor.execute('INSERT INTO classrooms(number, capacity, buildingId) VALUES(?, ?, ?);', (number, capacity, buildingId))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a classroom; Error message: {e}; Data: {(number, capacity, buildingId)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a classroom; Error message: {e}')
  db.commit()
  return True

# [id, number, capacity]
def getAllClassroomsForBuilding(buildingId: int) -> list[list[int, int, int]]:
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    classrooms = cursor.execute('SELECT * FROM classrooms WHERE buildingId=?;', (buildingId,))
    classrooms = classrooms.fetchall()
    db.commit()
    return classrooms
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting all classrooms; Error message: {e}; Data: {buildingId}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting all classrooms; Error message: {e}')
  db.commit()
  return []

def getClassroomId(number: int, buildingId: int) -> int:
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    classrooms = cursor.execute('SELECT * FROM classrooms WHERE number=? AND buildingId=?;', (number, buildingId))
    classrooms = classrooms.fetchone()
    db.commit()
    return classrooms
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting classroomId; Error message: {e}; Data: {(number, buildingId)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting classroomId; Error message: {e}')
  db.commit()
  return []



def addCourse(name: str, strId: str):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    cursor.execute('INSERT INTO courses(name, strIdentifier) VALUES(?, ?);', (name, strId))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a course; Error message: {e}; Data: {(name, strId)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a course; Error message: {e}')
  db.commit()
  return True

def getAllCourses():
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    courses = cursor.execute('SELECT * FROM courses;')
    courses = courses.fetchall()
    db.commit()
    return courses
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting all courses; Error message: {e};')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting all courses; Error message: {e}')
  db.commit()
  return []



def addRole(role: str):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    cursor.execute('INSERT INTO roles(role) VALUES(?);', (role,))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a role; Error message: {e}; Data: {(role)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a role; Error message: {e}')
  db.commit()
  return True

def getAllRoles():
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    roles = cursor.execute('SELECT * FROM roles;')
    roles = roles.fetchall()
    db.commit()
    return roles
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting all roles; Error message: {e};')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting all roles; Error message: {e}')
  db.commit()
  return []



def addPerson(birthNumber: int, roleId: int, firstName: str, lastName: str):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    cursor.execute('INSERT OR IGNORE INTO names(name) VALUES(?)', (firstName,))
    cursor.execute('INSERT OR IGNORE INTO names(name) VALUES(?)', (lastName,))
    fnId = cursor.execute('SELECT id FROM names WHERE name=?', (firstName,))
    fnId = fnId.fetchone()[0]
    lnId = cursor.execute('SELECT id FROM names WHERE name=?', (lastName,))
    lnId = lnId.fetchone()[0]
    cursor.execute('INSERT INTO people(birthNumber, roleId, firstNameId, lastNameId) VALUES(?, ?, ?, ?)', (birthNumber, roleId, fnId, lnId))
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a person; Error message: {e}; Data: {(birthNumber, roleId, firstName, lastName)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a person; Error message: {e}')
  db.commit()
  return True

# [id, role, fname, lname]
def getPersonByBirthNumber(birthNumber: int) -> list[int, str, str, str]:
  try:
    db = sqlite3.connect(dbLocation)
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
    logger.log(f'An error in SQL syntax occurred while getting person; Error message: {e}; Data: {birthNumber}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting person; Error message: {e}')
  db.commit()
  return []

# [birthNumber, role, fname, lname]
def getPersonById(pid: int) -> list[int, str, str, str]:
  try:
    db = sqlite3.connect(dbLocation)
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
    logger.log(f'An error in SQL syntax occurred while getting person; Error message: {e}; Data: {pid}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting person; Error message: {e}')
  db.commit()
  return []

# [id, birthNumber, role, fname, lname]
def getAllPeopleWithName(firstName='', lastName='') -> list[list[int, int, str, str, str]]:
  try:
    if not firstName and not lastName: return []
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    data = ()
    if firstName and lastName:
      data = (firstName, lastName)
    else:
      data = (firstName,) if firstName else (lastName,)
    person = cursor.execute(f'''SELECT people.id, people.birthNumber, roles.role, fn.name, ln.name FROM people
                                                JOIN names fn ON fn.id=people.firstNameId
                                                JOIN names ln ON ln.id=people.lastNameId
                                                JOIN roles ON roles.id=people.roleId
                                                WHERE {"fn.name=?" if firstName else ""} {"AND" if firstName and lastName else ""} {"ln.name=?" if lastName else ""};''', data)
    person = person.fetchall()
    db.commit()
    return person
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while getting person; Error message: {e}; Data: {firstName, lastName}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting person; Error message: {e}')
  db.commit()
  return []

# [id, birthNumber, fname, lname]
def getAllPeopleWithRole(role: str) -> list[list[int, int, str, str]]:
  try:
    db = sqlite3.connect(dbLocation)
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
    logger.log(f'An error in SQL syntax occurred while getting person; Error message: {e}; Data: {role}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while getting person; Error message: {e}')
  db.commit()
  return []











# Log in a user; returns id (if fail -> id = -1)
def logInUser(username, password):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    # Get id, salt and password of a username
    account = cursor.execute('SELECT id, salt, password, disabled FROM accounts WHERE username = ?;', (username,))
    account = account.fetchone()
    db.commit()
    # Check if the username exists
    if account:
      # Check if the account is disabled
      if account[3] == 1:
        return -1
      # Check if the password is right
      if (checkHashedPassword(password, account[1], account[2])):
        return account[0]
      else:
        logger.log(f'Password didn\'t match for user {username}', 2)
    else:
      logger.log(f'Unknown username: {username}', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while logging in a user; Error message: {e}; Data: {(username, password)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while logging in a user; Error message: {e}')
  db.commit()
  return -1


# Return True if Username was found in table
def checkIfUsernameExists(username):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    # If username is in accounts
    res1 = cursor.execute('SELECT * FROM accounts WHERE username = ?;', (username,))
    res1 = res1.fetchall()
    db.commit()
    if res1:
      return True
    return False
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while checking if a username already exists; Error message: {e}; Data: {(username)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while checking if a username already exists; Error message: {e}')
  db.commit()
  return True


def addUser(username, password):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    # Hash the password
    salt, hashed = hashPassword(password)
    # Data for INSERT
    data = (username, salt, hashed)
    # INSERT into accounts table
    cursor.execute('INSERT INTO accounts(username, salt, password) VALUES(?, ?, ?);', data)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while adding a user; Error message: {e}; Data: {(username, salt, password)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while adding a user; Error message: {e}')
  db.commit()
  return True


# Remove a user
def removeUser(ix):
  try:
    db = sqlite3.connect(dbLocation)
    cursor = db.cursor()
    # Find a user
    user = cursor.execute('SELECT username FROM accounts WHERE id = ?;', (ix,))
    user = user.fetchone()
    if user:
      cursor.execute('DELETE FROM accounts WHERE id = ?', (ix,))
    else:
      # If we were unable to find the id in accounts, we log it as a warning
      logger.log(f'Recieved remove request for id({ix}), however requested row is not present in accounts table aborting', 2)
  except sqlite3.Error as e:
    logger.log(f'An error in SQL syntax occurred while removing a user; Error message: {e}; Data: {(ix)}')
  except Exception as e:
    logger.log(f'An unexpected error occurred while removing a user; Error message: {e}')
  db.commit()
  return True

initialize()
addRole('Student')
addRole('Teacher')
addPerson(123, 1, 'jarda', 'pravda')
addPerson(124, 2, 'mike', 'pravda')
addPerson(125, 1, 'mike', 'lost')
addPerson(126, 2, 'jarda', 'pravda')
print(getAllPeopleWithRole('Student'), getAllPeopleWithRole('Teacher'), getAllPeopleWithRole('janitor'), sep='\n')
