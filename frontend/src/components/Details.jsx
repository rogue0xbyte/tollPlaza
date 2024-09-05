import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import { identifyCar, topUpBalance, toggleStolenStatus, toggleExemptedStatus, resetDB, fetchCarFromImage, fetchCarDetails } from '../services/api';
import { wait } from '../utils/timer';

const Details = () => {

  const token = localStorage.getItem('token');
  if (!token){
    window.location.href = "/logout";
  }

  const [plateNumber, setPlateNumber] = useState('');
  const [details, setDetails] = useState(null);

  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [imageData, setImageData] = useState(null);
  const videoRef = useRef();

  const [topUpAmount, setTopUpAmount] = useState('');
  // const [deductionAmount, setDeductionAmount] = useState('');

  useEffect(() => {
    // Fetch available cameras when component mounts
    const fetchCameras = async () => {
      const cameras = await navigator.mediaDevices.enumerateDevices();
      setCameras(cameras.filter(device => device.kind === 'videoinput'));
    };
    fetchCameras();
  }, []);

  useEffect(() => {
    // Access selected camera stream when selectedCamera changes
    const getCameraStream = async () => {
      if (selectedCamera) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: selectedCamera.deviceId }
          });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (error) {
          console.error('Error accessing camera:', error);
        }
      }
    };
    getCameraStream();
  }, [selectedCamera]);

  const handleCapture = async () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d').drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');

    const base64Image = imageData.split(',')[1];
    
    console.log("Image Captured! Fetching Details...");
    toast.success("Image Captured! Fetching Details...");

    const data = await fetchCarFromImage(base64Image);

    if(data) {
      toast.success("Data fetched successfully!");
      setPlateNumber(data.license_plate_number);
    } else {
      toast.error("Error fetching license plate data!")
      console.log('Error fetching License Plate');
    }
  };

  const handleSubmit = async (e) => {
    try{
      e.preventDefault();
      console.log("Submit button clicked"); // Check if the function is being triggered
    }catch(error){console.log(error);}
    const data = await identifyCar(plateNumber);
    setDetails(data);
    console.log("Details Fetched Successfuly!");
  };

  const navigate = useNavigate();

  const handleReset = async () => {
    const confirmed = window.confirm('Are you sure you want to reset the database?');
    if (confirmed) {
      try {
        await resetDB();
        console.log('Database reset successfully.');
      } catch (error) {
        console.error('Error resetting database:', error);
      }
    } else {
      console.log('Database reset canceled by user.');
    }
  };


  return (


    <div className="glass main" style={{ display: 'flex' }}>
        <div className="row spacious glass login_box negateTopper" style={{ width: '45%' }}>
          <br/>
          <h2>Get Details from Number Plate</h2>
          <div className="row spacious">
            <form  onSubmit={handleSubmit} id="myForm" className="row spacious">
              <input type="text" placeholder="Enter Plate Number" value={plateNumber} onChange={(e) => setPlateNumber(e.target.value)} />
              <button type="submit">Get Details</button>
            </form>
          </div>
          <div className="row login_box negateTopper" style={{ width: '100%' }}>
            <h2>Select Camera</h2>
            <select onChange={(e) => setSelectedCamera(JSON.parse(e.target.value))}>
              <option value="">Select Camera</option>
              {cameras.map(camera => (
                <option key={camera.deviceId} value={JSON.stringify(camera)}>{camera.label}</option>
              ))}
            </select>
            {selectedCamera && (
              <div>
                <video ref={videoRef} autoPlay style={{ width: '100%', height: 'auto' }}></video>
                <br />
                <button onClick={handleCapture}>Capture</button>
                {imageData && <img src={imageData} alt="Captured" style={{ maxWidth: '100%' }} />}
              </div>
            )}
          </div>
          <br/><br/>
        </div>
        <div className="row glass login_box negateTopper" style={{ width: '45%' }}>
          <h2>Details</h2>
          {details && (
            <div>
              <p>Plate Number: {details.plate_number}</p>
              <p>Owner Name: {details.owner_name}</p>
              <p>Car Model: {details.car_model}</p>
              <p>Car Color: {details.car_color}</p>
              <p>Balance: {details.balance}</p>
              <p>Stolen: {details.stolen ? 'Yes' : 'No'}</p>
              <p>Exempted: {details.exempted ? 'Yes' : 'No'}</p>
            <div className="row spacious">
              <input type="text" placeholder="Top-Up Amount" value={topUpAmount} onChange={(e) => setTopUpAmount(e.target.value)}/>
              <button onClick={async () => {
                topUpBalance(topUpAmount, details.plate_number);
                await wait(0.05);
                handleSubmit();
              }}>
                Top-Up Balance
              </button>
            </div>
            <br/>
            {/* <div className="row spacious">
              <input type="text" placeholder="Deduction Amount" value={deductionAmount} onChange={(e) => setDeductionAmount(e.target.value)}/>
              <button onClick={async () => {
                topUpBalance(-topUpAmount, details.plate_number);
                await wait(0.05);
                handleSubmit();
              }}>
                Deduct Balance
              </button>
            </div>
            <br/> */}
            <div className="row spacious">
              <button onClick={async () => {
                toggleStolenStatus(details.plate_number);
                await wait(0.05);
                handleSubmit();
              }}>
                {details.stolen ? 'Unflag as Stolen' : 'Flag as Stolen'}
              </button>
            </div>
            <br/>
            <div className="row spacious">
              <button onClick={async () => {
                toggleExemptedStatus(details.plate_number);
                await wait(0.05);
                handleSubmit();
              }}>
                {details.stolen ? 'Unflag as Exempted' : 'Flag as Exempted'}
              </button>
            </div>
            </div>
          )}
          <button onClick={handleReset}>Reset DB</button>
        </div>
        <div><Toaster
          position="bottom-right"
          reverseOrder={false}
        /></div>
    </div>
  );
};

export default Details;