import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import 'datatables.net';

import './styles/styles.css'
import './styles/datatables.min.css'

import LogIn from './components/LogIn'
// import SignUp from './components/SignUp'
import Details from './components/Details'
import CarDetails from './components/CarDetails'
import UpdateCarDetails from './components/UpdateCarDetails'
import AddCarDetails from './components/AddCarDetails'
import History from './components/History'
import Navbar from './components/Navbar'
import LogOut from './components/LogOut'

import { fetchCarDetails } from './services/api';


const App = () => {

  fetchCarDetails()
    .then(carDetails => {
      if(carDetails.code){
        localStorage.removeItem('token');
      };
    })
    .catch(error => {
      localStorage.removeItem('token');
    });

  return (
   <div className="App">
      <Router>
        <div className="glass navbar">
          <div className="nav-logo">
              <p>Toll Plaza</p>
          </div>
          {<Navbar/>}
        </div>
        <Routes>
          <Route exact path="/" element={<LogIn/>} />
          {/*<Route exact path="/signup" element={<SignUp/>} />*/}
          <Route exact path="/login" element={<LogIn/>} />
          <Route exact path="/details" element={<Details/>} />
          <Route exact path="/cardetails" element={<CarDetails/>} />
          <Route exact path="/history/:plateNumber" element={<History/>} />
          <Route exact path="/update/:plateNumber" element={<UpdateCarDetails />} />
          <Route exact path="/add_car" element={<AddCarDetails />} />
          <Route exact path="/logout" element={<LogOut/>} />
        </Routes>
      </Router>
    </div>
  );
};

export default App;