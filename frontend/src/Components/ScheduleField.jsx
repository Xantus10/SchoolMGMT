import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks';
import { Stack, Button, Modal, Paper, Center, Text, Menu, TextInput, NativeSelect, NumberInput, Title, Group } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { constructClassId, checkNullArray } from '../Components/Util.jsx'


//       0            1        2      3      4            5            6              7                 8            9
// C: [fieldType, lectureId, dayId, timeId, evenWeek, teacherStrID, subjectStrID, buildingStrID, classroomNum, fullOrAB]
// T: [fieldType, lectureId, dayId, timeId, evenWeek, courseStrID, classStartYear, classGroupNumber, subjectStrID, buildingStrID, classroomNum, fullOrAB]
// R: [fieldType, lectureId, dayId, timeId, evenWeek, courseStrID, classStratYear, classGroupNumber, subjectStrID, teacherStrID, fullOrAB]
function ScheduleField({aClassId, aBuildingsList, aData=[], changeFullScheduleData=()=>{}, changeHalfScheduleData=()=>{}, divide=()=>{}, aClickable=false }) {

  const subjectTextSize = (aData[aData.length-1] === 'F') ? 'xl' : 'sm';

  const paperField = (
    <Paper shadow='md' p={(aData[aData.length-1] === 'F') ? 'sm' : 5} withBorder  w={70} h={(aData[aData.length-1] === 'F') ? 110 : 60}>
      <Center><Stack gap={(aData[aData.length-1] === 'F') ? 7 : 0}>
        {
          (aData[0] === 'E') ? (<></>) :
          (aData[0] === 'C') ? (<>
          <Text size={subjectTextSize}>{aData[6]}</Text>
          <Text size='xs'>{aData[7]+aData[8]}</Text>
          <Text size='xs'>{aData[5]}</Text>
          </>) :
          (aData[0] === 'T') ? (<>
            <Text size={subjectTextSize}>{aData[8]}</Text>
            <Text size='xs'>{aData[9]+aData[10]}</Text>
            <Text size='xs'>{constructClassId(aData[5], aData[6], aData[7], aData[aData.length-1])}</Text>
            </>) :
          (aData[0] === 'R') ? (<>
            <Text size={subjectTextSize}>{aData[8]}</Text>
            <Text size='xs'>{aData[9]}</Text>
            <Text size='xs'>{constructClassId(aData[5], aData[6], aData[7], aData[aData.length-1])}</Text>
            </>) :
          (<></>)
        }
      </Stack></Center>
    </Paper>)

  if (aClickable) {
    const form = useForm({
      mode:'uncontrolled',
      initialValues: {
        lectureId: aData[1], // passed
        classId: aClassId, // passed
        teacherId: 0, // from useEffect on strID
        subjectId: 0, // from nativeselect
        classroomId: 0, // Building + classnum passed
        FullOrAB: aData[aData.length-1] // passed
      }
    })

    form.setFieldValue('lectureId', aData[1])
    form.setFieldValue('classId', aClassId)
    form.setFieldValue('FullOrAB', aData[aData.length-1])

    const [modalDisclosure, setModalDisclosure] = useDisclosure(false)

    
    const [teacherStrId, setTeacherStrId] = useState('')
    const [foundTeacher, setFoundTeacher] = useState(<></>)

    const [teacherSubjects, setTeacherSubjects] = useState([])

    const [buildingId, setBuildingId] = useState(0)
    const [classroomNumber, setClassroomNumber] = useState(0)
    const [foundClassroom, setFoundClassroom] = useState(<></>)

    if (!checkNullArray(aBuildingsList) && buildingId === 0) setBuildingId(aBuildingsList[0].value)

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

    function getLabelByValue(objarr, val) {
      for (let i=0; i<objarr.length; i++) {
        if (objarr[i].value == val) return objarr[i].label;
      }
    }

    function setSchedule() { // ADD HANDLING FOR SPLIT LECTURES - WILL NOT USE CHANGEFULLSCHEDULEDATA, IMPLEMENT NEW METHOD
      const vals = form.getValues()
      let buildingStr = getLabelByValue(aBuildingsList, buildingId)
      let s = buildingStr.indexOf('[')
      let e = buildingStr.indexOf(']')
      if (aData[aData.length-1] === 'F') {
        changeFullScheduleData(aData[2]-1, aData[3], ['C', aData[1], aData[2], aData[3], aData[4], teacherStrId, getLabelByValue(teacherSubjects, vals.subjectId), buildingStr.substr(s+1, (e-s-1)), classroomNumber, 'F'])
      } else {
        changeHalfScheduleData(aData[2]-1, aData[3], aData[aData.length-1], ['C', aData[1], aData[2], aData[3], aData[4], teacherStrId, getLabelByValue(teacherSubjects, vals.subjectId), buildingStr.substr(s+1, (e-s-1)), classroomNumber, aData[aData.length-1]])
      }
    }

    function createSchedule() {
      if (form.validate().hasErrors) {
        return
      }
      axios.post(process.env.REACT_APP_BE_ADDR+'/createSchedule', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
        (resp) => {
          if (resp.data.status === 200) setSchedule();
          PostNotification(resp.data)
        }
      )
      setModalDisclosure.close()
    }

    return (<>
    <Menu>
      <Menu.Target>
        {paperField}
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Item onClick={setModalDisclosure.open}>
          <Text>Add lecture</Text>
        </Menu.Item>
        <Menu.Item onClick={()=>{divide(aData[2]-1, aData[3], aData[1], aData[4])}}>
          <Text>Divide</Text>
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
    <Modal opened={modalDisclosure} onClose={setModalDisclosure.close} title="Schedule Field">
      <TextInput label='Teacher StrID' value={teacherStrId} onChange={e => setTeacherStrId(e.target.value)} />
      <Paper shadow="xs" radius="xl" withBorder p="md">
        {foundTeacher}
      </Paper>
      <NativeSelect data={teacherSubjects} label="Select subject" key={form.key('subjectId')} {...form.getInputProps('subjectId')} />
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
    </>);
  }
  return paperField;
}

export default ScheduleField