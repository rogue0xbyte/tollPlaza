import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import $ from 'jquery';
import { fetchCarDetails, deleteCar } from '../services/api';

const CarDetails = () => {

  const token = localStorage.getItem('token');
  if (!token){
    window.location.href = "/logout";
  }

  const [carData, setCarData] = useState([]);
  const tableRef = useRef();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchCarDetails();
        setCarData(data);
      } catch (error) {
        console.error('Error fetching car details:', error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (carData.length > 0) {
      $(tableRef.current).DataTable();
    }
  }, [carData]);


  const navigate = useNavigate();

  const handleUpdate = (plateNumber) => {
    navigate(`/update/${plateNumber}`);
  };  

  return (
    <div className="glass main" style={{ padding: '30px' }}>
     <div className="row spacious">
      <h2>Car Details</h2>
      <button onClick={() => window.location.href = "/add_car"}>Add Car</button>
     </div>
     <br/>
      <table ref={tableRef} style={{ width: '100%' }}>
        <thead>
          <tr>
            <th>Plate Number</th>
            <th>Owner Name</th>
            <th>Car Model</th>
            <th>Car Color</th>
            <th>Balance</th>
            <th>Stolen?</th>
            <th>History</th>
            <th>Delete</th>
            <th>Update</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(carData) && carData.map((car) => (
            <tr key={car.plate_number}>
              <td>{car.plate_number}</td>
              <td>{car.owner_name}</td>
              <td>{car.car_model}</td>
              <td>{car.car_color}</td>
              <td>{car.balance}</td>
              <td>{car.stolen === 1 ? "Yes" : "No"}</td>
              <td>
                <button onClick={() => deleteCar(car.plate_number)}>Delete</button>
              </td>
              <td>
                <button onClick={ () => window.location.href = `/history/${car.plate_number}` }>History</button>
              </td>
              <td>
                <button onClick={() => handleUpdate(car.plate_number)}>Update</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CarDetails;