import { Link } from 'react-router-dom';

function StartPage() {
  return (
    <div className="StartPage">
      <header className="StartPage-header">
        <h1>Welcome to the Start Page</h1>
        <h3>Data available for registered user.</h3>
      </header>
      <ul>
        <li><Link to="/user/register">Register</Link></li>
        <li><Link to="/user/login">Login</Link></li>
        <li><Link to="/main">Go to Data Panel</Link></li>
      </ul>
    </div>
  );
}

export default StartPage;