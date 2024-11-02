import { Routes, Route } from 'react-router-dom'
import Cookies from 'js-cookie'

import IndexPage from './IndexPage.jsx'

import './App.css'

function App() {

  if (Cookies.get('JWT_token') === undefined) return <IndexPage />

  return (
    <>
      <Routes>
        <Route path='/' element={<IndexPage />}/>
      </Routes>
    </>
  )
}

export default App;
