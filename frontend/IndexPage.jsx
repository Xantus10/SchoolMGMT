import LoginForm from "./LoginForm";

import './indexPage.css'

function IndexPage() {

  return (
    <>
      <div className="container">
        <div className="index-content">
          <h1>SchoolMGMT</h1>
          <br />
          <p>SchoolMGMT is an easy to use web server application, that provides all the necessary tools for managing school.</p>
        </div>
        <div className="index-login">
          <LoginForm />
        </div>
      </div>
    </>
  );

}

export default IndexPage