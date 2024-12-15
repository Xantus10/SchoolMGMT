import React, { useState, useEffect, cloneElement } from 'react';
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
  const [lectures, setLectures] = useState([])
  const [buildingsList, setBuildingsList] = useState([])
  const [scheduleData, setScheduleData] = useState([])
  const [fullScheduleData, setFullScheduleData] = useState([])

  // Initial gets
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
    axios.get(process.env.REACT_APP_BE_ADDR+'/getLectures', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        if (resp.data.status === 200) {
          if (checkNullArray(resp.data.lectures)) return;
          setLectures(resp.data.lectures)
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
  }, [])

  // Get schedule when Id changes from last rerender
  useEffect( () => {
    if (aIdToFetch === 0) return;
    axios.get(process.env.REACT_APP_BE_ADDR+'/getSchedule', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {forWhat: aFieldType, rid: aIdToFetch}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          setScheduleData(resp.data.schedule)
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [aIdToFetch])

  // Get lectureId for day/time (initial gets HAVE to be notnull)
  function idForDayTime(d, t) {
    for (let i=0; i<lectures.length; i++) {
      if (lectures[i][1]===d && lectures[i][2]===t) return {lid:lectures[i][0],evenWeek:lectures[i][3]};
    }
  }

  function getIxForLectureId(lid) { // [lectureId, dayId, timeId, evenWeek, teacherStrID, subjectStrID, buildingStrID, classroomNum, fullOrAB]
    for (let i=0; i<scheduleData.length; i++) {
      if (scheduleData[i][0] === lid) return i;
    }
    return -1;
  }

  function changeFullScheduleData(iIx, jIx, data) {
    const tmp = fullScheduleData.slice();
    tmp[iIx][jIx] = data;
    setFullScheduleData(tmp)
  }

  // After initial gets and schedule data is (re)fetched call this
  useEffect( () => {
    if (days.length===0 || lectureTimes.length===0 || lectures.length===0) return;
    const tmp = new Array(days.length);
    for (let i=0; i<days.length; i++) {
      tmp[i] = new Array(lectureTimes.length)
      for (let j=0; j<lectureTimes.length; j++) {
        let {lid, evenWeek} = idForDayTime(days[i][0], lectureTimes[j][0])
        let ix = getIxForLectureId(lid)
        if (ix !== -1) {
          tmp[i][j] = [aFieldType, ...scheduleData[ix]]
        } else {
          tmp[i][j] = ['E', lid, i+1, j, evenWeek]
        }
      }
    }
    setFullScheduleData(tmp)
  }, [days, lectureTimes, lectures, scheduleData])

  

  return (
    <>
    <div className='grid-container' style={{gridTemplateColumns: `repeat(${lectureTimes.length+1}, 1fr)`, gridTemplateRows: `repeat(${days.length+1}, 1fr)`}}>
      <div className='grid-cell'></div>
      {lectureTimes.map((time) => <div className='grid-cell' key={time[0]}><LectureTimeField alectureId={time[0]} alectureTime={time[1]} /></div>)}
      {fullScheduleData.map((day, ix) => {return (<><div key={-1} className='grid-cell'>{days[ix][1]}</div>{...day.map((ldata) => {return (<div className='grid-cell' key={ldata[1]}><ScheduleField aData={ldata} changeFullScheduleData={changeFullScheduleData} aClassId={aIdToFetch} aBuildingsList={buildingsList} aClickable /></div>)})}</>)})}
    </div>
    </>
  );
}

export default Schedule