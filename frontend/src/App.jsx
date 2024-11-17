import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Cookies from 'js-cookie'

import IndexPage from './Pages/IndexPage.jsx'
import HomePage from './Pages/HomePage.jsx'
import NotFoundPage from './Pages/NotFoundPage.jsx'


function App() {

  if (Cookies.get('JWT_token') === undefined) return <IndexPage />

  return (
    <>
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
