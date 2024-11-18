import React, { useState } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, TextInput, Button, Group, Title, Text, PasswordInput } from '@mantine/core';

function AddAccount() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      birthNumber: '',
      username: '',
      password: '',
      rpass: ''
    },

    validate: {
      username: (un) => ((un.length>0) ? null : 'Enter username'),
      password: (p) => ((p.length<10) ? 'Password must be at least 10 characters' : (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/.test(p) ? null : 'Password must contain at least one uppercase, lowercase letter and a number')),
      birthNumber: (bn) => (/^\d{6}\/\d{3,4}$/.test(bn) ? null : 'Enter valid birth number'),
      rpass: (p, values) => ((p===values.password) ? null : "Passwords don't match")
    }
  })

  const [status, setStatus] = useState('')

  function createAccount() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createAccount', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        setStatus('Done!')
      }
    )
  }

  return (
    <>
    <Title order={2}>Add account</Title>
    <Stack w={'max-content'} gap={7}>
      <TextInput label="Birth number" placeholder='010101/2222' key={form.key('birthNumber')} {...form.getInputProps('birthNumber')} />
      <TextInput label="Username" placeholder='Martin10' key={form.key('username')} {...form.getInputProps('username')} />
      <PasswordInput label="Password" placeholder='Password123' key={form.key('password')} {...form.getInputProps('password')} />
      <PasswordInput label="Repeat password" placeholder='Password123' key={form.key('rpass')} {...form.getInputProps('rpass')} />
      <Group justify='flex-end'><Button onClick={createAccount}>Submit</Button></Group>
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddAccount