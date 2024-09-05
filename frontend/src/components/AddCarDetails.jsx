import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { addCarDetails, fetchCarDetails } from '../services/api';

const AddCarDetails = () => {

  const token = localStorage.getItem('token');
  if (!token){
    window.location.href = "/logout";
  }

  
  const [plateNumber, setPlateNumber] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [carModel, setCarModel] = useState('');
  const [carColor, setCarColor] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (addCarDetails(plateNumber, ownerName, carModel, carColor)) {
      toast.success("Added Car Successfuly!")
    } else {
      toast.error("Error adding car details :(")
    }
  };

  return (
    <div className="glass main">
     <div className="login_box" style={{ display:"block" }}>
      <h2>Add Car Details</h2><br/>
      <form onSubmit={handleSubmit}>
        <label>Plate Number:</label>
        <input type="text" value={plateNumber} onChange={(e) => setPlateNumber(e.target.value)} /><br/><br/>
        <label>Owner Name:</label>
        <input type="text" value={ownerName} onChange={(e) => setOwnerName(e.target.value)} /><br/><br/>
        <label>Car Model:</label>
        <input type="text" value={carModel} onChange={(e) => setCarModel(e.target.value)} /><br/><br/>
        <label>Car Color:</label>
        <input type="text" value={carColor} onChange={(e) => setCarColor(e.target.value)} /><br/><br/>
        <button type="submit">Add Car</button>
      </form>
     </div>
     <div><Toaster
        position="bottom-right"
        reverseOrder={false}
      /></div>
    </div>
  );
};

export default AddCarDetails;