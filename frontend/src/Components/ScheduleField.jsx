import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks';
import { Stack, Button, Modal, Paper, Center, Text, Menu, TextInput, NativeSelect, NumberInput, Title, Group } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { constructClassId, checkNullArray } from '../Components/Util.jsx'


// Field type: C for class | T for teachers | R for room | E for empty
function ScheduleField({ alectureId, aFieldType='E', aClassId, aBuildingsList, aData={teacherStrId: '', subjectStrID: '', buildingStrId: '', classroomNum: '', courseStrId: '', startYear: 0, group: null}, aClickable=false }) {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      lectureId: alectureId, // passed
      classId: aClassId, // passed
      teacherId: 0, // from useEffect on strID
      subjectId: 0, // from nativeselect
      classroomId: 0, // Building + classnum select
      FullOrAB: 'F' // Maybe will come from props
    }
  })

  const [modalDisclosure, setModalDisclosure] = useDisclosure(false)
  const [data, setData] = useState(aData)

  const [teacherStrId, setTeacherStrId] = useState('')
  const [foundTeacher, setFoundTeacher] = useState(<></>)

  const [teacherSubjects, setTeacherSubjects] = useState([])

  const [buildingId, setBuildingId] = useState(0)
  const [classroomNumber, setClassroomNumber] = useState(0)
  const [foundClassroom, setFoundClassroom] = useState(<></>)

  useEffect( () => {
    if (!aClickable || !modalDisclosure) return;
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
    if (!aClickable || form.getValues().teacherId===0) return;
    axios.get(process.env.REACT_APP_BE_ADDR+'/getSubjectsExpertiseForTeacher', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {'teacherId': form.getValues().teacherId}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.subjects)) {setTeacherSubjects([]); return;}
          setTeacherSubjects(resp.data.subjects.map((sub) => ({label: sub[1], value: sub[0]})))
          form.setFieldValue('subjectId', resp.data.subjects[0][0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [foundTeacher])

  useEffect( () => {
    if (!aClickable || !modalDisclosure) return;
    axios.get(process.env.REACT_APP_BE_ADDR+'/getClassroomId', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {'buildingId': buildingId, 'classroomNumber': classroomNumber}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.classroom)) return;
          setFoundClassroom(<Text>Classroom found ({resp.data.classroom[1]})</Text>)
          form.setFieldValue('classroomId', resp.data.classroom[0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [buildingId, classroomNumber])

  useEffect( () => {if (!checkNullArray(aBuildingsList)) setBuildingId(aBuildingsList[0].value)}, [aBuildingsList])

  function createSchedule() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createSchedule', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200); //setSchedule();
        PostNotification(resp.data)
      }
    )
    setModalDisclosure.close()
  }

  const paperField = (
  <Paper shadow='md' p='sm' withBorder  w={70} h={100}>
    <Center><Stack gap={7}>
      { (aFieldType === 'E') ? (<></>) : <>
      <Text size='xl'>{data.subjectStrID}</Text>
      <Text size='xs'>{(aFieldType !== 'R') ? (data.buildingStrId+data.classroomNum) : constructClassId(data.courseStrId, data.startYear, data.group)}</Text>
      <Text size='xs'>{(aFieldType !== 'T') ? (data.teacherStrId) : constructClassId(data.courseStrId, data.startYear, data.group)}</Text></>
      }
    </Stack></Center>
  </Paper>)

  return (
    <>
    {(aClickable) ? (<>
  <Menu>
    <Menu.Target>
      {paperField}
    </Menu.Target>
    <Menu.Dropdown>
      <Menu.Item onClick={setModalDisclosure.open}>
        <Text>Add lecture</Text>
      </Menu.Item>
      <Menu.Item onClick={()=>{}}>
        <Text>Divide</Text>
      </Menu.Item>
    </Menu.Dropdown>
  </Menu>
  <Modal opened={modalDisclosure} onClose={setModalDisclosure.close} title="Schedule Field">
    <TextInput label='Teacher StrID' value={teacherStrId} onChange={e => setTeacherStrId(e.target.value)} />
    <Paper shadow="xs" radius="xl" withBorder p="md">
      {foundTeacher}
    </Paper>
    <NativeSelect data={teacherSubjects} label="Select subject" />
    <Title order={5}>Classroom</Title>
      <Group>
      <NativeSelect label='Select building' data={aBuildingsList} value={buildingId} onChange={e => setBuildingId(e.currentTarget.value)} />
      <NumberInput label="Classroom number" value={classroomNumber} onChange={setClassroomNumber} />
      </Group>
      <Paper shadow="xs" radius="xl" withBorder p="md">
        {foundClassroom}
      </Paper>
    <Button onClick={createSchedule}>Create!</Button>
  </Modal>
  </>) : (
    <>{paperField}</>
  )}
    </>
  );
}

export default ScheduleField