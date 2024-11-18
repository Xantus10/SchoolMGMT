import React, { useState } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, TextInput, Button, Group, Title, Text, PasswordInput } from '@mantine/core';

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

  const [status, setStatus] = useState('')

  function createRole() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createRole', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        setStatus('Done!')
      }
    )
  }

  return (
    <>
    <Title order={2}>Add Role</Title>
    <Stack w={'max-content'} gap={7}>
      <TextInput label="Role" placeholder='Janitor, Technician' key={form.key('role')} {...form.getInputProps('role')} />
      <Group justify='flex-end'><Button onClick={createRole}>Submit</Button></Group>
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddRole