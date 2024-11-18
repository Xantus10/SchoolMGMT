import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useForm } from '@mantine/form';
import { Stack, NumberInput, NativeSelect, Button, Group, Title, Text } from '@mantine/core';

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
  const [status, setStatus] = useState('')

  useEffect(() => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getBuildings', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            setBuildingList(resp.data.buildings.map(building => ({label: `${building[1]} [${building[2]}]`, value: building[0]})));
            form.setFieldValue('buildingId', resp.data.buildings[0][0])
            break;
          case 401:
            setStatus('Unauthorized')
          case 403:
            setStatus('Not logged in!')
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
        switch (resp.data.status) {
          case 200:
            setStatus('Done!')
            break;
          case 401:
            setStatus('You are not logged in or your session has expired!')
            break;
          case 403:
            setStatus('You do not have sufficient privileges for this operation!')
            break;
          case 500:
            setStatus(resp.data.msg)
            break;
        }
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
      <Text>{status}</Text>
    </Stack>
    </>
  );
}

export default AddClassroom