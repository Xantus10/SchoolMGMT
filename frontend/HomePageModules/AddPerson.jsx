import React, { useState, useEffect } from 'react';
import axios from 'axios'

import './AddPerson.css'

function AddPerson() {
  const [birthNumber, setBirthNumber] = useState()
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [roleId, setRoleId] = useState(0)
  const [rolesList, setRolesList] = useState([])

  useEffect(() => {
    axios.get('http://localhost:5000/getAllRoles', {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        setRolesList(resp.data.roles.map(role => <option value={role[0]}>{role[1]}</option>));
      }
    )
  }, [])

  function createPerson() {
    axios.post('http://localhost:5000/createPerson', {birthNumber: birthNumber, firstName: firstName, lastName: lastName, roleId: roleId}, {headers: {"Content-Type": "application/json"}, withCredentials: true}).then(
      (resp) => {
        
      }
    )
  }

  return (
    <>
    <span>First name</span>
    <input type="text" placeholder='Jane' value={firstName} onChange={(e) => setFirstName(e.target.value)} />
    <span>Last name</span>
    <input type="text" placeholder='Doe' value={lastName} onChange={(e) => setLastName(e.target.value)} />
    <span>Birth number</span>
    <input type="number" placeholder='0123456789' value={birthNumber} onChange={(e) => setBirthNumber(e.target.value)} />
    <span>Role</span>
    <select value={roleId} onChange={(e) => setRoleId(e.target.value)}>
      {rolesList}
    </select>
    <button onClick={createPerson}></button>
    </>
  );
}

export default AddPerson