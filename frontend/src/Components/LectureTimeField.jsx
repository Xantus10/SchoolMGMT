import React, { useState } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks';
import { Stack, Button, Modal, Paper, Center, Text } from '@mantine/core';
import { TimeInput } from '@mantine/dates'
import { PostNotification } from '../Components/APINotifications';

function LectureTimeField({ alectureId, alectureTime=0 }) {
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
    <Paper onClick={setModalDisclosure.open} shadow='md' p='sm'>
      <Center><Stack gap={7}>
        <Text>{alectureId}</Text>
        <Text>{Math.floor(lectureTime/60)}:{lectureTime%60} - {Math.floor((lectureTime+45)/60)}:{(lectureTime+45)%60}</Text>
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