import { Group, Menu, Text, Button } from '@mantine/core';
import { useEffect } from 'react';
import Cookies from 'js-cookie'


import Schedule from '../../Components/Schedule';


function SubHomePageTeacher({setContent}) {

  useEffect(() => {
    if (Cookies.get('JWT_token') === undefined) {
        window.location.href = '/'
      }
    
    let token = JSON.parse(atob(Cookies.get('JWT_token').split('.')[0]))
    setContent(<Schedule aFieldType='T' aIdToFetch={token['uid']} />)
  }, [])
  
  return (
    <>
      <Group align='center' h={"100%"}>
          
      </Group>
    </>
  );
}

export default SubHomePageTeacher