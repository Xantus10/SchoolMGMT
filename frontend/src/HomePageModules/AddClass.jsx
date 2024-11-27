import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, NativeSelect, Button, Group, Title, Text, TextInput, Paper, NumberInput } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';

function AddClass() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      courseId: 0,
      startYear: new Date().getFullYear(),
      groupNumber: 0,
      rootClassroomId: 0,
      classTeacherId: 0
    },

    validate: {
      startYear: (sy) => ((sy >= 2000 && sy <= 9999) ? null : 'Year must be between 2000 and 9999'),
    }
  })

  const [teacherStrId, setTeacherStrId] = useState('')
  const [foundTeacher, setFoundTeacher] = useState(<></>)
  const [buildingId, setBuildingId] = useState(0)
  const [classroomNumber, setClassroomNumber] = useState(0)
  const [foundClassroom, setFoundClassroom] = useState(<></>)
  const [coursesList, setCoursesList] = useState([])
  const [buildingsList, setBuildingsList] = useState([])


  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getTeacherByStrId', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {'strId': teacherStrId}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (resp.data.teacher === undefined || resp.data.teacher === null) return;
          setFoundTeacher(<Text>{`${resp.data.teacher[2]}, ${resp.data.teacher[1]}`}</Text>)
          form.setFieldValue('classTeacherId', resp.data.teacher[0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [teacherStrId])

  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getClassroomId', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {'buildingId': buildingId, 'classroomNumber': classroomNumber}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (resp.data.classroom === undefined || resp.data.classroom === null) return;
          setFoundClassroom(<Text>Classroom found ({resp.data.classroom[1]})</Text>)
          form.setFieldValue('rootClassroomId', resp.data.classroom[0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [buildingId, classroomNumber])

  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getCourses', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (resp.data.courses === undefined || resp.data.courses[0] === undefined) return;
          setCoursesList(resp.data.courses.map(c => ({label: `${c[1]} [${c[2]}]`, value: c[0]})))
          form.setFieldValue('courseId', resp.data.courses[0][0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
    axios.get(process.env.REACT_APP_BE_ADDR+'/getBuildings', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          setBuildingsList(resp.data.buildings.map(building => ({label: `${building[1]} [${building[2]}]`, value: building[0]})));
          setBuildingId(resp.data.buildings[0][0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [])

  function createClass() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createClass', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        PostNotification(resp.data)
      }
    )
  }

  let groupData = [
    {label: 'No group ID', value: 0},
    {label: '1', value: 1},
    {label: '2', value: 2},
  ];

  return (
    <>
    <Title order={2}>Add class</Title>
    <Stack w={'max-content'} gap={7}>
      <NativeSelect label="Course" data={coursesList} key={form.key('courseId')} {...form.getInputProps('courseId')} />
      <NumberInput label="Starting year" min={2000} max={9999} key={form.key('startYear')} {...form.getInputProps('startYear')} />
      <NativeSelect label="Group number (to differentiate multiple classes)" data={groupData} key={form.key('groupNumber')} {...form.getInputProps('groupNumber')} />
      <Title order={4}>Root classroom</Title>
      <Group>
      <NativeSelect label='Select building' data={buildingsList} value={buildingId} onChange={e => setBuildingId(e.target.value)} />
      <NumberInput label="Classroom number" value={classroomNumber} onChange={setClassroomNumber} />
      </Group>
      <Paper shadow="xs" radius="xl" withBorder p="md">
        {foundClassroom}
      </Paper>
      <Title order={4}>Class teacher</Title>
      <TextInput label='Class teacher StrID' value={teacherStrId} onChange={e => setTeacherStrId(e.target.value)} />
      <Paper shadow="xs" radius="xl" withBorder p="md">
        {foundTeacher}
      </Paper>
      <Group justify='flex-end'><Button onClick={createClass}>Submit</Button></Group>
    </Stack>
    </>
  );
}

export default AddClass