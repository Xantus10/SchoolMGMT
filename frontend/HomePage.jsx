import React, { useState } from 'react'
import Cookies from 'js-cookie'

import SubHomePageAdmin from './SubHomePageAdmin.jsx'
import SubHomePageTeacher from './SubHomePageTeacher.jsx'
import SubHomePageStudent from './SubHomePageStudent.jsx'

import './HomePage.css'

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
  }

  return (
    <>
     <div className="home-header">
      <div>
        <h2>SchoolMGMT</h2>
      </div>
      <div>
        {moduleBar}
      </div>
     </div>
     <div className="home-content">
      {content}
     </div>
     <div className="home-footer">
      <p>Developed with react</p>
      <p>2024</p>
     </div>
    </>
  )
}

export default HomePage