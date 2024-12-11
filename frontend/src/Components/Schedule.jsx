import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { Stack, MultiSelect, Button, Group, Title, Text, TextInput, Paper, NumberInput } from '@mantine/core';
import { GetNotification, PostNotification } from '../Components/APINotifications';
import { checkNullArray } from '../Components/Util.jsx'
import ScheduleField from './ScheduleField.jsx';
import LectureTimeField from './LectureTimeField.jsx'

import './Schedule.css'


// Field type: C for class | T for teachers | R for room ; aIdToFetch=Id of teacher/class/room
function Schedule({ aEditable=false, aFieldType, aIdToFetch }) {

  const [days, setDays] = useState([])
  const [lectureTimes, setLectureTimes] = useState([])
  const [scheduleFields, setScheduleFields] = useState([])
  const [buildingsList, setBuildingsList] = useState([])


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
    if (aEditable) axios.get(process.env.REACT_APP_BE_ADDR+'/getBuildings', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.buildings)) return;
          setBuildingsList(resp.data.buildings.map(building => ({label: `${building[1]} [${building[2]}]`, value: building[0]})));
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
          tmp[i][j] = <div className='grid-cell'><ScheduleField alectureId={0} aFieldType='E' aClickable aBuildingsList={buildingsList} /></div>
        }
      };
      setScheduleFields(tmp)
    }
  }, [days, lectureTimes])


  return (
    <>
    <div className='grid-container' style={{gridTemplateColumns: `repeat(${lectureTimes.length+1}, 1fr)`, gridTemplateRows: `repeat(${days.length+1}, 1fr)`}}>
      <div className='grid-cell'></div>
      {lectureTimes.map((time) => <div className='grid-cell'><LectureTimeField key={time[0]} alectureId={time[0]} alectureTime={time[1]} /></div>)}
      {scheduleFields.map((dayList, i) => {
        return (<><div className='grid-cell'><Paper>{days[i][1]}</Paper></div>{dayList}</>)
      })}
    </div>
    </>
  );
}

export default Schedule