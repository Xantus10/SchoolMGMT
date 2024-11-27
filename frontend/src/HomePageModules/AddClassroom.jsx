import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, NumberInput, NativeSelect, Button, Group, Title, Text } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';

function AddClassroom() {
  const form = useForm({
    mode:'uncontrolled',
    initialValues: {
      number: 0,
      capacity: 0,
      buildingId: 0
    }
  })

  const [buildingList, setBuildingList] = useState([])

  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getBuildings', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          setBuildingList(resp.data.buildings.map(building => ({label: `${building[1]} [${building[2]}]`, value: building[0]})));
          form.setFieldValue('buildingId', resp.data.buildings[0][0])
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [])

  function createClassroom() {
    if (form.validate().hasErrors) {
      return
    }
    axios.post(process.env.REACT_APP_BE_ADDR+'/createClassroom', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        PostNotification(resp.data)
      }
    )
  }

  return (
    <>
    <Title order={2}>Add classroom</Title>
    <Stack w={'max-content'} gap={7}>
      <NumberInput hideControls allowNegative={false} label="Classroom number" key={form.key('number')} {...form.getInputProps('number')} />
      <NumberInput hideControls allowNegative={false} label="Capacity" key={form.key('capacity')} {...form.getInputProps('capacity')} />
      <NativeSelect label="Building" data={buildingList} key={form.key('buildingId')} {...form.getInputProps('buildingId')} />
      <Group justify='flex-end'><Button onClick={createClassroom}>Submit</Button></Group>
    </Stack>
    </>
  );
}

export default AddClassroom