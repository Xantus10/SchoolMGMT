import { Group, Menu, Text, Button } from '@mantine/core';

import AddAccount from '../../HomePageModules/AddAccount.jsx';
import AddPerson from '../../HomePageModules/AddPerson.jsx';
import AddBuilding from '../../HomePageModules/AddBuilding.jsx';
import AddClassroom from '../../HomePageModules/AddClassroom.jsx';


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
          <Menu.Divider />
          <Menu.Label>
            People
          </Menu.Label>
          <Menu.Item onClick={e => setContent(<AddPerson />)}>
            <Text>Add person</Text>
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
    </Group>
    </>
  );
}

export default SubHomePageAdmin