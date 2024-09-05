import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, useParams } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import { updateCarDetails, fetchCarDetails } from '../services/api';

const UpdateCarDetails = () => {

  const token = localStorage.getItem('token');
  if (!token){
    window.location.href = "/logout";
  }

  const { plateNumber } = useParams();
  const [ownerName, setOwnerName] = useState('');
  const [carModel, setCarModel] = useState('');
  const [carColor, setCarColor] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (updateCarDetails(plateNumber, ownerName, carModel, carColor)){
      toast.success("Updated Successfuly!");
    } else {
      toast.error("Error updating!");
    }
  };

  return (
    <div className="glass main">
     <div className="login_box" style={{ display:"block" }}>
      <h2>Update Car Details</h2><br/>
      <form onSubmit={handleSubmit}>
        <label>Owner Name:</label>
        <input type="text" value={ownerName} onChange={(e) => setOwnerName(e.target.value)} /><br/><br/>
        <label>Car Model:</label>
        <input type="text" value={carModel} onChange={(e) => setCarModel(e.target.value)} /><br/><br/>
        <label>Car Color:</label>
        <input type="text" value={carColor} onChange={(e) => setCarColor(e.target.value)} /><br/><br/>
        <button type="submit">Update</button>
      </form>
     </div>

      <div><Toaster
        position="bottom-right"
        reverseOrder={false}
      /></div>
    </div>
  );
};

export default UpdateCarDetails;