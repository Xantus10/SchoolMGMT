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
  const [scheduleFields, setScheduleFields] = useState([])
  const [buildingsList, setBuildingsList] = useState([])
  const [scheduleData, setScheduleData] = useState([])
  const [fetchStatus, setFetchStatus] = useState(0)


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

  useEffect( () => {
    axios.get(process.env.REACT_APP_BE_ADDR+'/getSchedule', {headers: {"Content-Type": "application/json"}, withCredentials: true, params: {forWhat: aFieldType, rid: aIdToFetch}}).then(
      (resp) => {
        if (resp.data.status === 200) {
          setFetchStatus((prev) => prev+1)
          if (checkNullArray(resp.data.schedule)) return;
          setScheduleData(resp.data.schedule)
        } else {
          GetNotification(resp.data)
        }
      }
    )
  }, [aIdToFetch])

  function idForDayTime(d, t) {
    for (let i=0; i<lectures.length; i++) {
      if (lectures[i][1]===d && lectures[i][2]===t) return lectures[i][0];
    }
  }

  useEffect( () => {
    if (days.length > 0 && lectureTimes.length > 0 && lectures.length > 0) {
      const tmp = new Array(days.length);
      for (let i=0; i<days.length; i++) {
        tmp[i] = new Array(lectureTimes.length)
        for (let j=0; j<lectureTimes.length; j++) {
          tmp[i][j] = <div className='grid-cell'><ScheduleField alectureId={idForDayTime(days[i][0], lectureTimes[j][0])} aFieldType='E' aClickable aBuildingsList={buildingsList} aClassId={aIdToFetch} /></div>
        }
      };
      setScheduleFields(tmp)
      setFetchStatus((prev) => prev+1)
    }
  }, [days, lectureTimes, lectures])

  useEffect( () => { // [lectureId, dayId, timeId, evenWeek, teacherStrID, subjectStrID, buildingStrID, classroomNum, fullOrAB]
    if (fetchStatus<2) return;
    const tmp = scheduleFields
    if (aFieldType==='C') {
      scheduleData.forEach((data) => {
        tmp[data[1]-1][data[2]] = <div className='grid-cell'><ScheduleField alectureId={data[0]} aFieldType={aFieldType} aClickable aBuildingsList={buildingsList} aClassId={aIdToFetch} aData={{teacherStrId: data[4], subjectStrID: data[5], buildingStrId: data[6], classroomNum: data[7]}} /></div>
      })
    } else if (aFieldType==='T') {

    } else if (aFieldType==='R') {

    }
    setScheduleFields(tmp)
    setFetchStatus(1)
  }, [fetchStatus])

  return (
    <>
    <div className='grid-container' style={{gridTemplateColumns: `repeat(${lectureTimes.length+1}, 1fr)`, gridTemplateRows: `repeat(${days.length+1}, 1fr)`}}>
      <div className='grid-cell'></div>
      {lectureTimes.map((time) => <div className='grid-cell'><LectureTimeField key={time[0]} alectureId={time[0]} alectureTime={time[1]} /></div>)}
      {scheduleFields.map((dayList, i) => {
        return (<><div className='grid-cell'><Paper>{days[i][1]}</Paper></div>{...dayList}</>)
      })}
    </div>
    </>
  );
}

export default Schedule