import { Group, Menu, Text, Button } from '@mantine/core';

import AddAccount from '../../HomePageModules/AddAccount.jsx'
import AddPerson from '../../HomePageModules/AddPerson.jsx'


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
    </Group>
    </>
  );
}

export default SubHomePageAdmin