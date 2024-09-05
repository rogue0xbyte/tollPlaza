import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { signUpAdmin } from '../services/api';

const SignUp = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (signUpAdmin(username, password)) {
      console.log(response.data);
      toast.success(response.data.message);
    } else {
      toast.error("Couldn't Sign Up.")
    }
  };

  return (

    <div className="glass main">
    <div className="row spacious">
          <div className=" glass login_box" style={{ width: '45%' }}>
        <h2>Sign Up</h2>
        <form  onSubmit={handleSubmit}>
          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} /><br/><br/>
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} /><br/><br/>
          <button type="submit">Sign Up</button>
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

export default SignUp;