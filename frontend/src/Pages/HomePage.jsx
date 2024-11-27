import React, { useState, useEffect } from 'react'
import { Stack, Box, Title, Text, Group, Button } from '@mantine/core'
import { useInterval } from '@mantine/hooks'
import Cookies from 'js-cookie'

import SubHomePageAdmin from './SubHomePage/SubHomePageAdmin.jsx'
import SubHomePageTeacher from './SubHomePage/SubHomePageTeacher.jsx'
import SubHomePageStudent from './SubHomePage/SubHomePageStudent.jsx'
import SubHomePageNotFound from './SubHomePage/SubHomePageNotFound.jsx'
import axios from 'axios'


function HomePage() {
  const [content, setContent] = useState(<></>)
  const [logoutCounter, setLogoutCounter] = useState(0)
  const i = useInterval(() => setLogoutCounter((prev) => prev+1), 5000)

  useEffect(() => {
    i.start()
    return i.stop
  }, [])

  useEffect(() => {
    const events = ['click', 'mousemove', 'keypress', 'scroll']

    const update = () => {setLogoutCounter(0)}

    events.forEach((event) => window.addEventListener(event, update))

    return () => {events.forEach((event) => window.removeEventListener(event, update))}
  })

  useEffect(() => {
    if (logoutCounter > 120) {
      logout()
    }
  }, [logoutCounter])

  if (Cookies.get('JWT_token') === undefined) {
    window.location.href = '/'
  }

  let token = JSON.parse(atob(Cookies.get('JWT_token').split('.')[0]))
  let moduleBar = <></>
  switch (token['role']) {
    case 'admin':
      moduleBar = <SubHomePageAdmin setContent={setContent} />
      break;
    case 'teacher':
      moduleBar = <SubHomePageTeacher setContent={setContent} />
      break;
    case 'student':
      moduleBar = <SubHomePageStudent setContent={setContent} />
      break;
    default:
      moduleBar = <SubHomePageNotFound setContent={setContent} />
      break;
  }

  function logout() {
    axios.post(process.env.REACT_APP_BE_ADDR+'/logout', {}, {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        window.location.href = '/'
      })
  }

// header modulebar content footer
  return (
    <>
    <Stack h={"100vh"}>
      <Box h={"10vh"} bg={"cyan.6"} p={20}>
        <Group>
          <Title c={"gray.0"}>SchoolMGMT</Title>
          <Button bg={'red.9'} ml="auto" onClick={logout}>Logout</Button>
        </Group>
      </Box>
      <Box h={"5vh"} bg={'cyan.2'} pl={10}>
        {moduleBar}
      </Box>
      <Box h={"80vh"} p={20}>
        {content}
      </Box>
      <Box h={"5vh"}>
        <Group justify="space-around">
          <Text size='sm'>SchoolMGMT</Text>
          <Text size='sm'>2024</Text>
        </Group>
      </Box>
    </Stack>
    </>
  )
}

export default HomePage