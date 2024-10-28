import { Routes, Route } from 'react-router-dom'
import IndexPage from './IndexPage.jsx'
import LoginPage from './LoginPage.jsx'
import './App.css'

function App() {
  return (
    <>
      <Routes>
        <Route path='/' element={<IndexPage />}/>
        <Route path='/login' element={<LoginPage />}/>
      </Routes>
    </>
  )
}

export default App;
