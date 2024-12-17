import React, { useState, useEffect, cloneElement } from 'react';
import axios from 'axios'
import { GetNotification, ErrorNotification } from '../Components/APINotifications';
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
    let arr = new Array()
    for (let i=0; i<scheduleData.length; i++) {
      if (scheduleData[i][0] === lid) arr.push(i);
    }
    return arr;
  }

  function changeFullScheduleData(iIx, jIx, data) {
    const tmp = fullScheduleData.slice();
    tmp[iIx][jIx] = data;
    setFullScheduleData(tmp)
  }

  function changeHalfScheduleData(iIx, jIx, half, data) {
    const tmp = fullScheduleData.slice();
    if (half === 'A') {
      tmp[iIx][jIx] = ['S', {B: tmp[iIx][jIx][1].B, A: data}];
    } else {
      tmp[iIx][jIx] = ['S', {A: tmp[iIx][jIx][1].A, B: data}];
    }
    setFullScheduleData(tmp)
  }

  function splitLecture(iIX, jIx, lid, evenWeek) { // Split lecture structure - [fieldType:'S', {'A': [dataforAhalf], 'B': [dataforBhalf]}]
    if (fullScheduleData[iIX][jIx][0] !== 'E') ErrorNotification('You cannot split non-empty lecture');
    const tmp = fullScheduleData.slice();
    tmp[iIX][jIx] = ['S', {A: ['E', lid, iIX+1, jIx, evenWeek, 'A'], B: ['E', lid, iIX+1, jIx, evenWeek, 'B']}]
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
        switch (ix.length) {
          case 0:
            tmp[i][j] = ['E', lid, i+1, j, evenWeek, 'F']
            break;
          case 1:
              let half = scheduleData[ix[0]][scheduleData[ix[0]].length-1];
              if (half === 'F') {
                tmp[i][j] = [aFieldType, ...scheduleData[ix[0]]]
                break;
              } else if (half === 'A') {
                tmp[i][j] = ['S', {A: [aFieldType, ...scheduleData[ix[0]]], B: ['E', lid, i+1, j, evenWeek, 'B']}]
              } else {
                tmp[i][j] = ['S', {B: [aFieldType, ...scheduleData[ix[0]]], A: ['E', lid, i+1, j, evenWeek, 'A']}]
              }
              break;
          case 2:
            tmp[i][j] = ['S', {A: [aFieldType, ...scheduleData[ix[0]]], B: [aFieldType, ...scheduleData[ix[1]]]}]
            break;
        }
      }
    }
    setFullScheduleData(tmp)
  }, [days, lectureTimes, lectures, scheduleData])


  return (
    <>
    <div className='grid-container' style={{gridTemplateColumns: `repeat(${lectureTimes.length+1}, 1fr)`, gridTemplateRows: `repeat(${days.length+1}, 1fr)`}}>
      <div className='grid-cell' key={-100}></div>
      {lectureTimes.map((time) => <div className='grid-cell' key={-time[0]-days.length}><LectureTimeField alectureId={time[0]} alectureTime={time[1]} /></div>)}
      {fullScheduleData.map((day, ix) => {
        return (<><div className='grid-cell' key={-days[ix][0]}>{days[ix][1]}</div>{...day.map((ldata) => {
          if (ldata[0] === 'S') {
            return (
              <div className='grid-cell' key={ldata[1].A[1]}>
                <ScheduleField aData={ldata[1].A} changeHalfScheduleData={changeHalfScheduleData} aClassId={aIdToFetch} aBuildingsList={buildingsList} aClickable={aEditable} />
                <ScheduleField aData={ldata[1].B} changeHalfScheduleData={changeHalfScheduleData} aClassId={aIdToFetch} aBuildingsList={buildingsList} aClickable={aEditable} />
              </div>
            )
          }
          return (<div className='grid-cell' key={ldata[1]}><ScheduleField aData={ldata} changeFullScheduleData={changeFullScheduleData} divide={splitLecture} aClassId={aIdToFetch} aBuildingsList={buildingsList} aClickable={aEditable} /></div>)
        })}</>)
      })}
    </div>
    </>
  );
}

export default Schedule