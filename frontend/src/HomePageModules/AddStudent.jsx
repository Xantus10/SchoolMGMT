import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, NativeSelect, Button, Group, Title, TextInput } from '@mantine/core';
import { notifications } from '@mantine/notifications'
import { BiCheckCircle, BiErrorAlt } from "react-icons/bi";

function AddStudent() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      personId: 0,
      classId: 0,
      half: 'A'
    }
  })

  const [pFirstName, setPFirstName] = useState('')
  const [pLastName, setPLastName] = useState('')
  const [peopleList, setPeopleList] = useState([])
  const [classesList, setClassesList] = useState([])


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
            notifications.show({
              title: 'Unauthorized',
              message: '',
              color: 'red.9',
              icon: <BiErrorAlt />
            })
          case 403:
            notifications.show({
              title: 'Not logged in!',
              message: '',
              color: 'red.9',
              icon: <BiErrorAlt />
            })
        }
      }
    )
  }, [pFirstName, pLastName])

  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getClasses', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            if (resp.data.classes === undefined || resp.data.classes[0] === undefined) return;
            let now = new Date()
            now.setMonth(now.getMonth()-8)
            setClassesList(resp.data.classes.map(c => ({label: `${c[1]}${now.getFullYear()-c[2]+1}${(c[3] === null) ? '' : c[3]}`, value: c[0]})));
            form.setFieldValue('classId', resp.data.classes[0][0])
            break;
          case 401:
            notifications.show({
              title: 'Unauthorized',
              message: '',
              color: 'red.9',
              icon: <BiErrorAlt />
            })
          case 403:
            notifications.show({
              title: 'Not logged in!',
              message: '',
              color: 'red.9',
              icon: <BiErrorAlt />
            })
        }
      }
    )
  }, [])

  function createStudent() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createStudent', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            notifications.show({
              title: 'Done',
              message: '',
              color: 'lime.8',
              icon: <BiCheckCircle />
            })
            break;
          case 401:
            notifications.show({
              title: 'You are not logged in or your session has expired!',
              message: '',
              color: 'red.9',
              icon: <BiErrorAlt />
            })
            break;
          case 403:
            notifications.show({
              title: 'You do not have sufficient privileges for this operation!',
              message: '',
              color: 'red.9',
              icon: <BiErrorAlt />
            })
            break;
          case 500:
            notifications.show({
              title: resp.data.msg,
              message: '',
              autoClose: false,
              withCloseButton: true,
              color: 'red.9',
              icon: <BiErrorAlt />
            })
            break;
        }
      }
    )
  }

  return (
    <>
    <Title order={2}>Add Student</Title>
    <Stack w={'max-content'} gap={7}>
      <Title order={4}>Select person</Title>
      <Group>
        <TextInput label="First name" placeholder='Jane' value={pFirstName} onChange={e => setPFirstName(e.target.value)} />
        <TextInput label="Last name" placeholder='Doe' value={pLastName} onChange={e => setPLastName(e.target.value)} />
      </Group>
      <NativeSelect label="Person" data={peopleList} key={form.key('personId')} {...form.getInputProps('personId')} />
      <NativeSelect label="Class" data={classesList} key={form.key('classId')} {...form.getInputProps('classId')} />
      <NativeSelect label="Half" data={['A', 'B']} key={form.key('half')} {...form.getInputProps('half')}/>
      <Group justify='flex-end'><Button onClick={createStudent}>Submit</Button></Group>
    </Stack>
    </>
  );
}

export default AddStudent