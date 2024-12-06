import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { Stack, NumberInput, NativeSelect, Button, Group, Title, Text } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { checkNullArray } from '../Components/Util';
import LectureTimeField from '../Components/LectureTimeField';

function AddLectureTime() {

  const [timesList, setTimesList] = useState([])

  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getLectureTimes', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          const tmp = Array(10).fill(0).map((v, i) => <LectureTimeField key={i} alectureId={i} />);
          if (!checkNullArray(resp.data.times)) resp.data.times.forEach((time) => (tmp[time[0]]=<LectureTimeField key={time[0]} alectureId={time[0]} alectureTime={time[1]} />));
          setTimesList(tmp)
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [])

  function initializeLectures() {
    axios.post(process.env.REACT_APP_BE_ADDR+'/initializeLectures', {}, {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        PostNotification(resp.data)
      }
    )
  }

  return (
    <>
    <Title order={2}>Manage lecture times</Title>
    <Group>{timesList}</Group>
    <Button onClick={initializeLectures}>Click here to apply</Button>
    </>
  );
}

export default AddLectureTime