import React, { useState } from "react";
import axios from 'axios';


function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState(0);
  const API_KEY = '5vtb{$&(@WI%^tvbU6*TY&%VTBt7^B&Ivt7i5tbv&;`W/o0)';

  function handleUsernameInput(event) {
    setUsername(event.target.value);
  }
  
  function handlePasswordInput(event) {
    setPassword(event.target.value);
  }

  function register() {
    axios.post('http://localhost:5000/createAccount', {username: username, password: password, API_KEY: API_KEY}, {headers: {"Content-Type": "application/json"}}).then(
      (resp) => setStatus(resp.data.status)
    )
  }

  function login() {

  }

  return (
    <>
      <h1>Log in</h1>
      <input type="text" placeholder="Username" value={username} onChange={handleUsernameInput} /><br />
      <input type="password" placeholder="Password" value={password} onChange={handlePasswordInput} /><br />
      <button onClick={login}>Log in</button>
      <button onClick={register}>Register</button><br />
      <p>{status}</p>
    </>
  );

}

export default LoginPage