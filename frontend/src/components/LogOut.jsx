import { clearToken } from '../utils/auth';

const LogOut = () => {
  return (
    <div>
      <h2>Log Out</h2>
      { clearToken() }
      { window.location.href = "/" }
    </div>
  );
};

export default LogOut;