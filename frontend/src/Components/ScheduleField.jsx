import React, { useState } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks';
import { Stack, Button, Modal, Paper, Center, Text } from '@mantine/core';
import { PostNotification } from '../Components/APINotifications';
import { constructClassId } from '../Components/Util.jsx'


// Field type: C for class | T for teachers | R for room
function ScheduleField({ alectureId, aFieldType='C', aData={teacherStrId: '', subjectStrID: '', buildingStrId: '', classroomNum: '', courseStrId: '', startYear: 0, group: null}, aClickable=false }) {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      lectureId: alectureId,
    }
  })

  const [modalDisclosure, setModalDisclosure] = useDisclosure(false)
  const [data, setData] = useState(aData)

  function createSchedule() {
    if (form.validate().hasErrors) {
      return
    }
    let tmp = form.getValues().time.split(':')
    axios.post(process.env.REACT_APP_BE_ADDR+'/createSchedule', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) setSchedule();
        PostNotification(resp.data)
      }
    )
    setModalDisclosure.close()
  }

  return (
    <>
    <Paper onClick={(aClickable) ? setModalDisclosure.open : ()=>{}} shadow='md' p='sm'>
      <Center><Stack gap={7}>
        <Text size='xl'>{data.subjectStrID}</Text>
        <Text size='xs'>{(aFieldType !== 'R') ? (data.buildingStrId+data.classroomNum) : constructClassId(data.courseStrId, data.startYear, data.group)}</Text>
        <Text size='xs'>{(aFieldType !== 'T') ? (data.teacherStrId) : constructClassId(data.courseStrId, data.startYear, data.group)}</Text>
      </Stack></Center>
    </Paper>
    <Modal opened={modalDisclosure} onClose={setModalDisclosure.close} title="Schedule Field" p="xl">
      <Text>FORM</Text>
      <Button onClick={createSchedule}>Create!</Button>
    </Modal>
    </>
  );
}

export default ScheduleField