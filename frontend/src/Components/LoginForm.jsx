import React, { useState } from "react";
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { Drawer, Button, TextInput, PasswordInput, Text } from "@mantine/core";
import axios from 'axios';


function LoginForm() {
  const [drawerState, setDrawerState] = useDisclosure(false)
  const [status, setStatus] = useState("");

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      username: '',
      password: ''
    }
  })

  function login() {
    axios.post(process.env.REACT_APP_BE_ADDR+'/login', form.getValues(), {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            setStatus(<>OK Redirecting... <a href="/home">Click here if you are not redirected</a></>)
            window.location.href = '/home'
            break;
          case 401:
            setStatus('Incorrect username or password!')
            break;
          default:
            setStatus('Unknown error has occured!')
        }
      }
    )
  }

  return (
    <>
    <Drawer opened={drawerState} onClose={setDrawerState.close} title="Login" position="right">
      <TextInput label="Username" placeholder="user" key={form.key('username')} {...form.getInputProps('username')} />
      <PasswordInput label="Password" placeholder="pass123" key={form.key('password')} {...form.getInputProps('password')} />
      <Button onClick={login} mt={20}>Login</Button>
      <Text>{status}</Text>
    </Drawer>
    <Button onClick={setDrawerState.open}>Login</Button>
    </>
  );

}

export default LoginForm