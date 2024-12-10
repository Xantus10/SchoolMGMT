import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { Stack, MultiSelect, Button, Group, Title, Text, TextInput, Paper, NumberInput } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { checkNullArray } from '../Components/Util.jsx'
import ScheduleField from './ScheduleField.jsx';


// Field type: C for class | T for teachers | R for room ; aIdToFetch=Id of teacher/class/room
function Schedule({ aEditable=false, aFieldType, aIdToFetch }) {

  const [days, setDays] = useState([])
  const [lectureTimes, setLectureTimes] = useState([])
  const [scheduleFields, setScheduleFields] = useState([])

  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getDays', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.days)) return;
          setDays(resp.data.days)
        } else {
          GetNotification(resp.data)
        }
      }
    )
    axios.get(process.env.REACT_APP_BE_ADDR+'/getLectureTimes', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.times)) return;
          setLectureTimes(resp.data.times)
        } else {
          GetNotification(resp.data)
        }
      }
    )
    /*axios.get(process.env.REACT_APP_BE_ADDR+'/getSchedule', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.times)) return;
          setLectureTimes(resp.data.times)
        } else {
          GetNotification(resp.data)
        }
      }
    )*/
  }, [])

  useEffect( () => {
    if (days.length > 0 && lectureTimes.length > 0) {
      const tmp = new Array(days.length);
      for (let i=0; i<days.length; i++) {
        tmp[i] = new Array(lectureTimes.length)
        for (let j=0; j<lectureTimes.length; j++) {
          tmp[i][j] = <ScheduleField alectureId={0} aFieldType='C' aClassId={1} aData={{buildingStrId: 'HAB', classroomNum: 118, subjectStrID: 'MAT', teacherStrId: 'SIN'}} aClickable />
        }
      };
      setScheduleFields(tmp)
    }
  }, [days, lectureTimes])


  return (
    <>
    {scheduleFields[0]}
    </>
  );
}

export default Schedule