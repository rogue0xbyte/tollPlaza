import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { logInAdmin } from '../services/api';

const LogIn = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');


  const token = localStorage.getItem('token');
  if (token){
    window.location.href = "/details";
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (await logInAdmin(username, password)) {
      toast.success("Logged In!");
      window.location.href = "/details";
    } else {
      toast.error("Log-In Failed!");
    }
  };

  return (
    <div className="glass main">
    <div className="row spacious">
          <div className=" glass login_box" style={{ width: '45%' }}>
        <h2>Log In</h2>
        <form  onSubmit={handleSubmit}>
          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} /><br/><br/>
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} /><br/><br/>
          <button type="submit">Log In</button>
        </form>
        </div>
      </div>
      <div><Toaster
        position="bottom-right"
        reverseOrder={false}
      /></div>
    </div>
  );
};

export default LogIn;