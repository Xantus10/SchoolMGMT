import React, { useState } from "react";
import axios from 'axios';

import './loginForm.css'


function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");

  function handleUsernameInput(event) {
    setUsername(event.target.value);
  }
  
  function handlePasswordInput(event) {
    setPassword(event.target.value);
  }

  function login() {
    axios.post('http://localhost:5000/login', {username: username, password: password}, {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        switch (resp.data.status) {
          case 200:
            setStatus(<>OK Redirecting... <a href="/home">Click here if you are not redirected</a></>)
            window.location.href = '/home'
            break;
          case 403:
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
    <div className="login-form-box">
      <span className="login-form-text">Username</span>
      <input type="text" placeholder="Username" value={username} onChange={handleUsernameInput} />
      <span className="login-form-text">Password</span>
      <input type="password" placeholder="Password" value={password} onChange={handlePasswordInput} />
      <button className="login-form-button" onClick={login}>Log in</button>
      <p>{status}</p>
    </div>
    </>
  );

}

export default LoginForm