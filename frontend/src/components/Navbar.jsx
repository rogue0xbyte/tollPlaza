import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate, useParams } from 'react-router-dom';

function Navbar() {
  const [hasToken, setHasToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    const handleStorageChange = () => {
      setHasToken(localStorage.getItem('token'));
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return (
    <div className="nav-links">
      {!hasToken && (
        <>
          {/* <Link to="/signup">Sign Up</Link>
          <Link to="/login">Log In</Link> */}
        </>
      )}
      {hasToken && (
        <>
          <Link to="/details">Get Details</Link>
          <Link to="/cardetails">Car DB</Link>
          <Link to="/logout">Log Out</Link>
        </>
      )}
    </div>
  );
}

export default Navbar;