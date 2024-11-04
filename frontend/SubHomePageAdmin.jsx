import AddAccount from './HomePageModules/AddAccount.jsx'

import './HomePage.css'

function SubHomePageAdmin({setContent}) {
  
  return (
    <div className='home-module-bar'>
      <div className="home-dropdown">
        <div className="home-dropdown-visible">
          <span>Accounting</span>
        </div>
        <div className="home-dropdown-content">
          <button onClick={e => setContent(<AddAccount />)}>Add account</button>
        </div>
      </div>
    </div>
  );
}

export default SubHomePageAdmin