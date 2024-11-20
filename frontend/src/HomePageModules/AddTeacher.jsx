import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, NativeSelect, Button, Group, Title, Text, TextInput } from '@mantine/core';
import { DatePickerInput } from '@mantine/dates'

function AddTeacher() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      personId: 0,
      teachingFrom: new Date(),
      strId: ""
    },

    validate: {
      teachingFrom: (tf) => (/^\d{4}-\d{2}-\d{2}$/.test(tf.toISOString().substring(0,10)) ? null : 'Date format invalid'),
      strId: (s) => (s.length === 3 ? null : 'String ID must be 3 characters')
    }
  })

  const [status, setStatus] = useState('')
  const [pFirstName, setPFirstName] = useState('')
  const [pLastName, setPLastName] = useState('')
  const [EmployeesList, setEmployeesList] = useState([])


  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getEmployeesByNames', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {...(pFirstName!=='' && {'firstName': pFirstName}), ...(pLastName!=='' && {'lastName': pLastName})}}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            if (resp.data.employees === undefined || resp.data.employees[0] === undefined) return;
            setEmployeesList(resp.data.employees.map(p => ({label: `${p[3]} ${p[4]} [${p[1]}]`, value: p[0]})));
            form.setFieldValue('personId', resp.data.employees[0][0])
            break;
          case 401:
            setStatus('Unauthorized')
          case 403:
            setStatus('Not logged in!')
        }
      }
    )
  }, [pFirstName, pLastName])

  function createTeacher() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createTeacher', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            setStatus('Done!')
            break;
          case 401:
            setStatus('You are not logged in or your session has expired!')
            break;
          case 403:
            setStatus('You do not have sufficient privileges for this operation!')
            break;
          case 500:
            setStatus(resp.data.msg)
            break;
        }
      }
    )
  }

  return (
    <>
    <Title order={2}>Add teacher</Title>
    <Stack w={'max-content'} gap={7}>
      <Title order={4}>Select person</Title>
      <Group>
        <TextInput label="First name" placeholder='Jane' value={pFirstName} onChange={e => setPFirstName(e.target.value)} />
        <TextInput label="Last name" placeholder='Doe' value={pLastName} onChange={e => setPLastName(e.target.value)} />
      </Group>
      <NativeSelect label="Person" data={EmployeesList} key={form.key('personId')} {...form.getInputProps('personId')} />
      <DatePickerInput label="Teaching from" placeholder='Pick a date' valueFormat='YYYY-MM-DD' key={form.key('teachingFrom')} {...form.getInputProps('teachingFrom')} />
      <TextInput label="Teacher identificator (3 characters)" placeholder='ABC' key={form.key('strId')} {...form.getInputProps('strId')} />
      <Group justify='flex-end'><Button onClick={createTeacher}>Submit</Button></Group>
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddTeacher