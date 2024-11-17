import React, { useState } from 'react'
import { Stack, Box, Title, Text, Group } from '@mantine/core'
import Cookies from 'js-cookie'

import SubHomePageAdmin from './SubHomePage/SubHomePageAdmin.jsx'
import SubHomePageTeacher from './SubHomePage/SubHomePageTeacher.jsx'
import SubHomePageStudent from './SubHomePage/SubHomePageStudent.jsx'
import SubHomePageNotFound from './SubHomePage/SubHomePageNotFound.jsx'


function HomePage() {
  const [content, setContent] = useState(<></>)

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
// header modulebar content footer
  return (
    <>
    <Stack h={"100vh"}>
      <Box h={"10vh"} bg={"cyan.6"} p={20}>
        <Title c={"gray.0"}>SchoolMGMT</Title>
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