import React, { useState } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks';
import { Stack, Button, Modal, Paper, Center, Text } from '@mantine/core';
import { TimeInput } from '@mantine/dates'
import { PostNotification } from '../Components/APINotifications';
import { stampToTime } from './Util';

function LectureTimeField({ alectureId, alectureTime=0, aClickable=false }) {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      lectureId: alectureId,
      time: alectureTime
    }
  })

  const [modalDisclosure, setModalDisclosure] = useDisclosure(false)
  const [lectureTime, setLectureTime] = useState(alectureTime)

  function createLectureTime() {
    if (form.validate().hasErrors) {
      return
    }
    let tmp = form.getValues().time.split(':')
    axios.post(process.env.REACT_APP_BE_ADDR+'/createLectureTime', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) setLectureTime(Number(tmp[0])*60+Number(tmp[1]));
        PostNotification(resp.data)
      }
    )
    setModalDisclosure.close()
  }

  return (
    <>
    <Paper onClick={(aClickable) ? setModalDisclosure.open : ()=>{}} shadow='md' p='sm'>
      <Center><Stack gap={7}>
        <Text>{alectureId}</Text>
        <Text>{stampToTime(lectureTime)} - {(lectureTime!==0) ? stampToTime(lectureTime+45) : ''}</Text>
      </Stack></Center>
    </Paper>
    <Modal opened={modalDisclosure} onClose={setModalDisclosure.close} title="Lecture" p="xl">
      <TimeInput label="Start time of the lecture" key={form.key('time')} {...form.getInputProps('time')} />
      <Button onClick={createLectureTime}>Create!</Button>
    </Modal>
    </>
  );
}

export default LectureTimeField