import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, MultiSelect, Button, Group, Title, Text, TextInput, Paper } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { checkNullArray } from '../Components/Util.jsx'
import DisplayTeacherSubjects from '../Components/DisplayTeacherSubjects.jsx';


function AddTeacherSubjectExpertise() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      teacherId: 0,
      subjectId: []
    },

  })

  const [teacherStrId, setTeacherStrId] = useState('')
  const [foundTeacher, setFoundTeacher] = useState(<></>)
  const [allSubjectsList, setAllSubjectsList] = useState([])
  const [subjectsList, setSubjectsList] = useState([])
  const [teacherSubjects, setTeacherSubjects] = useState([])
  const [reRender, setReRender] = useState()


  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getTeacherByStrId', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {'strId': teacherStrId}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.teacher)) return;
          form.setFieldValue('teacherId', resp.data.teacher[0])
          setFoundTeacher(<Text>{`${resp.data.teacher[2]}, ${resp.data.teacher[1]}`}</Text>)
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [teacherStrId])

  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getSubjects', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.subjects)) return;
          setAllSubjectsList(resp.data.subjects)
          setSubjectsList(resp.data.subjects.map((sub) => ({label: sub[2], value: sub[0].toString()})))
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [])

  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getSubjectsExpertiseForTeacher', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {'teacherId': form.getValues().teacherId}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.subjects)) {setTeacherSubjects([]); return;}
          setTeacherSubjects(resp.data.subjects)
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [foundTeacher, reRender])

  useEffect( () => {
    const tmpSubjectsList = allSubjectsList.slice()
    teacherSubjects.forEach((val) => {
      let i = 0
      let found = -1
      while (i < tmpSubjectsList.length && found === -1) {
        if (tmpSubjectsList[i][0] === val[0]) found = i;
        i++
      }
      if (found !== -1) tmpSubjectsList.splice(found, 1);
    })
    setSubjectsList(tmpSubjectsList.map((sub) => ({label: sub[2], value: sub[0].toString()})))
  }, [teacherSubjects])

  function createTeacherSubjectExpertise() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createTeacherSubject', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        PostNotification(resp.data)
        form.setFieldValue('subjectId', [])
        if (resp.data.status === 200) setReRender((old) => old+1)
      }
    )
  }

  return (
    <>
    <Title order={2}>Add subject expertise to teacher</Title>
    <Stack w={'max-content'} gap={7}>
      <Title order={4}>Teacher</Title>
      <TextInput label='Teacher StrID' value={teacherStrId} onChange={e => setTeacherStrId(e.target.value)} />
      <Paper shadow="xs" radius="xl" withBorder p="md">
        {foundTeacher}
      </Paper>
      <Text>Already has expertise in</Text>
      <DisplayTeacherSubjects subjects={teacherSubjects} />
      <MultiSelect data={subjectsList} label="Add subjects" key={form.key('subjectId')} {...form.getInputProps('subjectId')} clearable searchable maxDropdownHeight={300} />
      <Group justify='flex-end'><Button onClick={createTeacherSubjectExpertise}>Submit</Button></Group>
    </Stack>
    </>
  );
}

export default AddTeacherSubjectExpertise