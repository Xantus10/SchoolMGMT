import { Group, Menu, Text, Button } from '@mantine/core';

import AddAccount from '../../HomePageModules/AddAccount.jsx';
import AddPerson from '../../HomePageModules/AddPerson.jsx';
import AddBuilding from '../../HomePageModules/AddBuilding.jsx';
import AddClassroom from '../../HomePageModules/AddClassroom.jsx';
import AddCourse from '../../HomePageModules/AddCourse.jsx';
import AddRole from '../../HomePageModules/AddRole.jsx';
import AddEmployee from '../../HomePageModules/AddEmployee.jsx';
import AddTeacher from '../../HomePageModules/AddTeacher.jsx';
import AddClass from '../../HomePageModules/AddClass.jsx';
import AddStudent from '../../HomePageModules/AddStudent.jsx';
import AddSubject from '../../HomePageModules/AddSubject.jsx';
import AddTeacherSubjectExpertise from '../../HomePageModules/AddTeacherSubjectExpertise.jsx';
import AddLectureTime from '../../HomePageModules/AddLectureTimes.jsx';
import AddSchedule from '../../HomePageModules/AddSchedule.jsx';


function SubHomePageAdmin({setContent}) {
  
  return (
    <>
    <Group align='center' h={"100%"}>
      <Menu>
        <Menu.Target>
          <Button>People &amp; Accounts</Button>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Label>
            Accounts
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddAccount />)}>
            <Text>Add account</Text>
          </Menu.Item>
          <Menu.Item onClick={e => setContent(<AddRole />)}>
            <Text>Add role</Text>
          </Menu.Item>
          <Menu.Divider />
          <Menu.Label>
            People
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddPerson />)}>
            <Text>Add person</Text>
          </Menu.Item>
          <Menu.Item onClick={e => setContent(<AddEmployee />)}>
            <Text>Add employee</Text>
          </Menu.Item>
          <Menu.Item onClick={e => setContent(<AddTeacher />)}>
            <Text>Add teacher</Text>
          </Menu.Item>
          <Menu.Item onClick={e => setContent(<AddStudent />)}>
            <Text>Add student</Text>
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>
      <Menu>
        <Menu.Target>
          <Button>Buildings &amp; Classrooms</Button>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Label>
            Buildings
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddBuilding />)}>
            <Text>Add building</Text>
          </Menu.Item>
          <Menu.Divider />
          <Menu.Label>
            Classrooms
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddClassroom />)}>
            <Text>Add classroom</Text>
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>
      <Menu>
        <Menu.Target>
          <Button>Classes</Button>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Label>
            Courses
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddCourse />)}>
            <Text>Add course</Text>
          </Menu.Item>
          <Menu.Divider />
          <Menu.Label>
            Classes
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddClass />)}>
            <Text>Add class</Text>
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>
      <Menu>
        <Menu.Target>
          <Button>Subjects &amp; Schedules</Button>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Label>
            Subjects
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddSubject />)}>
            <Text>Add subject</Text>
          </Menu.Item>
          <Menu.Item onClick={e => setContent(<AddTeacherSubjectExpertise />)}>
            <Text>Add teacher expertise</Text>
          </Menu.Item>
          <Menu.Divider />
          <Menu.Label>
            Schedules
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddLectureTime />)}>
            <Text>Lecture times</Text>
          </Menu.Item>
          <Menu.Item onClick={e => setContent(<AddSchedule />)}>
            <Text>Add schedule</Text>
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>
    </Group>
    </>
  );
}

export default SubHomePageAdmin