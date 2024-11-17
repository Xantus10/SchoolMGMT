import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, TextInput, NativeSelect, Button, Group, Title, Text } from '@mantine/core';

function AddPerson() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      birthNumber: '',
      firstName: '',
      lastName: '',
      roleId: 0
    },

    validate: {
      firstName: (fn) => ((fn.length>0) ? null : 'Enter first name'),
      lastName: (ln) => ((ln.length>0) ? null : 'Enter last name'),
      birthNumber: (bn) => (/^\d{6}\/\d{3,4}$/.test(bn) ? null : 'Enter valid birth number')
    }
  })

  const [rolesList, setRolesList] = useState([])
  const [status, setStatus] = useState('')

  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getRoles', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        setRolesList(resp.data.roles.map(role => ({label: role[1], value: role[0]})));
      }
    )
  }, [])

  function createPerson() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createPerson', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        setStatus('Done!')
      }
    )
  }

  return (
    <>
    <Title order={2}>Add person</Title>
    <Stack w={'max-content'} gap={7}>
      <TextInput label="Birth number" placeholder='010101/2222' key={form.key('birthNumber')} {...form.getInputProps('birthNumber')} />
      <TextInput label="First name" placeholder='Jane' key={form.key('firstName')} {...form.getInputProps('firstName')} />
      <TextInput label="Last name" placeholder='Doe' key={form.key('lastName')} {...form.getInputProps('lastName')} />
      <NativeSelect label="Role" description="Be careful" data={rolesList} key={form.key('roleId')} {...form.getInputProps('roleId')} />
      <Group justify='flex-end'><Button onClick={createPerson}>Submit</Button></Group>
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddPerson