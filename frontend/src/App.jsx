import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Notifications } from '@mantine/notifications'
import Cookies from 'js-cookie'

import IndexPage from './Pages/IndexPage.jsx'
import HomePage from './Pages/HomePage.jsx'
import NotFoundPage from './Pages/NotFoundPage.jsx'


function App() {

  if (Cookies.get('JWT_token') === undefined) return <IndexPage />

  return (
    <>
    <Notifications position='bottom-left' limit={5} autoClose={4000} />
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<IndexPage />}/>
        <Route path='/home' element={<HomePage />}/>
        <Route path='*' element={<NotFoundPage/>}/>
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App;
