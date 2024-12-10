import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { Stack, MultiSelect, Button, Group, Title, Text, TextInput, Paper, NumberInput } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { checkNullArray } from '../Components/Util.jsx'
import ScheduleField from './ScheduleField.jsx';


// Field type: C for class | T for teachers | R for room | E for empty ; aIdToFetch=Id of teacher/class/room
function Schedule({ aEditable=false, aFieldType, aIdToFetch }) {

  const [days, setDays] = useState([])
  const [lectureTimes, setLectureTimes] = useState([])
  const [scheduleData, setScheduleData] = useState([])

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
    if (days.length > 0 && lectureTimes.length > 0) {
      const tmp = new Array(days.length);
      tmp.forEach((val, i) => {
        tmp[i] = new Array(lectureTimes.length); tmp[i].forEach((valj, j) => {
          tmp[i][j] = <ScheduleField />
        })
      });
    }
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


  return (
    <>
    
    </>
  );
}

export default Schedule