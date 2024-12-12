import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { Stack, NativeSelect, Title } from '@mantine/core';
import { GetNotification } from '../Components/APINotifications';
import { checkNullArray, constructClassId } from '../Components/Util';
import Schedule from '../Components/Schedule';

function AddSchedule() {

  const [classesList, setClassesList] = useState([])
  const [classId, setClassId] = useState(0)


  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getClasses', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.classes)) return;
          let now = new Date()
          now.setMonth(now.getMonth()-8)
          setClassesList(resp.data.classes.map(c => ({label: constructClassId(c[1], c[2], c[3]), value: c[0]})));
          setClassId(resp.data.classes[0][0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [])

  return (
    <>
    <Title order={2}>Add schedule</Title>
    <Stack w={'max-content'} gap={7}>
      <NativeSelect label="Class" data={classesList} value={classId} onChange={(e) => setClassId(e.target.value)} />
    </Stack>
    <Schedule aFieldType='C' aIdToFetch={classId} aEditable />
    </>
  );
}

export default AddSchedule