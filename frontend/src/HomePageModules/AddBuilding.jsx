import React, { useState } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, TextInput, Button, Group, Title, Text, PasswordInput } from '@mantine/core';

function AddBuilding() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      name: '',
      strId: ''
    },

    validate: {
      name: (n) => ((n.length>0) ? null : "Enter a name"),
      strId: (s) => ((s.length === 0) ? "Enter an identifcator" : (s.length < 5 ? null : "Identificator should be shorter than 5 characters"))
    }
  })

  const [status, setStatus] = useState('')

  function createBuilding() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createBuilding', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        setStatus('Done!')
      }
    )
  }

  return (
    <>
    <Title order={2}>Add building</Title>
    <Stack w={'max-content'} gap={7}>
      <TextInput label="Name" placeholder='Building A' key={form.key('name')} {...form.getInputProps('name')} />
      <TextInput label="String identifier" description="Identifier should be short and comprehensive" key={form.key('strId')} {...form.getInputProps('strId')} />
      <Group justify='flex-end'><Button onClick={createBuilding}>Submit</Button></Group>
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddBuilding