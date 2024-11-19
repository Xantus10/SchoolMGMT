import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, NativeSelect, Button, Group, Title, Text, Checkbox, TextInput } from '@mantine/core';

function AddEmployee() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      personId: 0,
      withSupervisor: false,
      supervisorId: 0
    }
  })

  const [status, setStatus] = useState('')
  const [pFirstName, setPFirstName] = useState('')
  const [pLastName, setPLastName] = useState('')
  const [eFirstName, setEFirstName] = useState('')
  const [eLastName, setELastName] = useState('')
  const [peopleList, setPeopleList] = useState([])
  const [employeeList, setEmployeeList] = useState([])


  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getPeopleByNames', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {...(pFirstName!=='' && {'firstName': pFirstName}), ...(pLastName!=='' && {'lastName': pLastName})}}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            if (resp.data.people === undefined || resp.data.people[0] === undefined) return;
            setPeopleList(resp.data.people.map(p => ({label: `${p[3]} ${p[4]} [${p[1]}]`, value: p[0]})));
            form.setFieldValue('personId', resp.data.people[0][0])
            break;
          case 401:
            setStatus('Unauthorized')
          case 403:
            setStatus('Not logged in!')
        }
      }
    )
  }, [pFirstName, pLastName])

  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getEmployeesByNames', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {...(eFirstName!=='' && {'firstName': eFirstName}), ...(eLastName!=='' && {'lastName': eLastName})}}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            if (resp.data.employees === undefined || resp.data.employees[0] === undefined) return;
            setEmployeeList(resp.data.employees.map(p => ({label: `${p[3]} ${p[4]} [${p[1]}]`, value: p[0]})));
            form.setFieldValue('supervisorId', resp.data.employees[0][0])
            break;
          case 401:
            setStatus('Unauthorized')
          case 403:
            setStatus('Not logged in!')
        }
      }
    )
  }, [eFirstName, eLastName])

  function createEmployee() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createEmployee', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
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
    <Title order={2}>Add employee</Title>
    <Stack w={'max-content'} gap={7}>
      <Title order={4}>Select person</Title>
      <Group>
        <TextInput label="First name" placeholder='Jane' value={pFirstName} onChange={e => setPFirstName(e.target.value)} />
        <TextInput label="Last name" placeholder='Doe' value={pLastName} onChange={e => setPLastName(e.target.value)} />
      </Group>
      <NativeSelect label="Person" data={peopleList} key={form.key('personId')} {...form.getInputProps('personId')} />
      <Title order={4}>Select supervisor</Title>
      <Checkbox label="Employee has a supervisor" key={form.key('withSupervisor')} {...form.getInputProps('withSupervisor', {type: 'checkbox'})} />
      <Group>
        <TextInput label="First name" placeholder='Jane' value={eFirstName} onChange={e => setEFirstName(e.target.value)} disabled={!form.getValues().withSupervisor} />
        <TextInput label="Last name" placeholder='Doe' value={eLastName} onChange={e => setELastName(e.target.value)} disabled={!form.getValues().withSupervisor} />
      </Group>
      <NativeSelect label="Supervisor" data={employeeList} key={form.key('supervisorId')} {...form.getInputProps('supervisorId')} disabled={!form.getValues().withSupervisor} />
      <Group justify='flex-end'><Button onClick={createEmployee}>Submit</Button></Group>
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddEmployee