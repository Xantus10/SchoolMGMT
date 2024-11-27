import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, TextInput, Button, Group, Title, Text, PasswordInput } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';

function AddRole() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      role: '',
      strId: ''
    },

    validate: {
      role: (r) => ((r.length>0) ? null : "Enter a role"),
    }
  })


  function createRole() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createRole', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        PostNotification(resp.data)
      }
    )
  }

  return (
    <>
    <Title order={2}>Add Role</Title>
    <Stack w={'max-content'} gap={7}>
      <TextInput label="Role" placeholder='Janitor, Technician' key={form.key('role')} {...form.getInputProps('role')} />
      <Group justify='flex-end'><Button onClick={createRole}>Submit</Button></Group>
    </Stack>
    </>
  );
}

export default AddRole