import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Routes, useParams } from 'react-router-dom';
import $ from 'jquery';
import { fetchCarHistory, fetchCarDetails } from '../services/api';

const CarDetails = () => {

  const token = localStorage.getItem('token');
  if (!token){
    window.location.href = "/logout";
  }
  
  const { plateNumber } = useParams();
  const [carData, setCarData] = useState([]);
  const tableRef = useRef();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchCarHistory(plateNumber);
        setCarData(data.data);
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

  return (
    <div className="glass main" style={{ padding: '30px' }}>
     <div className="row spacious">
      <h2>Car History</h2>
     </div>
     <br/>
      <table ref={tableRef} style={{ width: '100%' }}>
        <thead>
          <tr>
            <th>Plate Number</th>
            <th>Event Type</th>
            <th>Event Description</th>
            <th>Toll Booth</th>
            <th>Event Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(carData) && carData.map((car) => (
            <tr key={car.car_id}>
              <td>{car.car_id}</td>
              <td>{car.event_type}</td>
              <td>{car.event_description}</td>
              <td>{car.toll_booth}</td>
              <td>{car.event_timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CarDetails;