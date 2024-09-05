import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'localhost:8081'

function App() {
  const [carDetails, setCarDetails] = useState(null);
  const [cameraFeed, setCameraFeed] = useState(null);
  const [ws, setWs] = useState(null);
  const [loading, setLoading] = useState(true); // State to track loading status
  const [fetchDetailsInterval, setFetchDetailsInterval] = useState(null); // State to hold interval ID

  useEffect(() => {
    // Establish WebSocket connection for camera feed
    const cameraSocket = new WebSocket(`ws://${API_URL}/ws/camera`);
    cameraSocket.onopen = () => {
      console.log("Connected to camera websocket");
      setLoading(false); // Update loading status when connected
    };
    cameraSocket.onmessage = (event) => {
      // Received frame from camera websocket
      setCameraFeed("data:image/jpeg;base64," + event.data);
    };
    setWs(cameraSocket);

    // Fetch car details from backend API
    const intervalId = setInterval(fetchCarDetails, 1000);
    setFetchDetailsInterval(intervalId);

    return () => {
      // Cleanup function
      cameraSocket.close();
      clearInterval(intervalId);
    };
  }, []);

  const fetchCarDetails = async () => {
    try {
      const response = await fetch(`http://${API_URL}/api/car/details`);
      if (!response.ok) {
        throw new Error('Failed to fetch car details');
      }
      const data = await response.json();
      setCarDetails(data);
    } catch (error) {
      console.error('Error fetching car details:', error);
      setCarDetails(null); // Reset car details on error
    }
  };

  const handleStop = async () => {
    // Disconnect WebSocket and stop car checking loop
    if (ws) {
      ws.close();
    }
    const response = await fetch(`http://${API_URL}/api/stop-mqtt`);
    clearInterval(fetchDetailsInterval);
    if (!response.ok) {
        throw new Error('Failed to publish MQTT STOP');
    }
  };

  const handleStart = async () => {
    // Reload the app
    const response = await fetch(`http://${API_URL}/api/start-mqtt`);
    window.location.reload();
  };

  return (
    <div className="App">
      <header dir="rtl"><img src="https://i.imgur.com/mvs9mgW.png" className="header-image"/></header>
      <main>
        {loading ? ( // Display loading screen if loading is true
          <div className="loading-screen">
            <iframe src="https://giphy.com/embed/uIJBFZoOaifHf52MER" onMouseOver={void(0)} width="480" height="439" frameBorder="0" className="giphy-embed" allowFullScreen></iframe>
          </div>
        ) : (
          <div className="content-container">
            <section className="live-feed">
              {cameraFeed && (
                <div className="image-overlay">
                  <img src={cameraFeed} alt="Camera Feed" />
                  <div className="car-details-overlay">
                    {carDetails ? ( // Check if carDetails is not null
                      <div>
                        <h2>Owner Details</h2>
                        <p>Owner Name: {carDetails.owner_name}</p>
                        <p>Plate Number: {carDetails.plate_number}</p>
                        <p>Car Model: {carDetails.car_model}</p>
                        <p>Car Color: {carDetails.car_color}</p>
                        <p>Balance: {carDetails.balance} AED</p>
                        <p>Status: {carDetails.stolen ? <span style={{color: 'red', textTransform: 'uppercase'}}>مسروق - Stolen</span> : <span style={{color: 'green'}}>غير مسروق - Not Stolen</span>}</p>
                        <p>Exempted: {carDetails.exempted ? <span style={{textTransform: 'uppercase'}}>Exempted!</span> : <span>Not Exempted</span>}</p>
                      </div>
                    ) : (
                      <p>No cars found in frame</p>
                    )}
                  </div>
                </div>
              )}
            </section>
          </div>
        )}
        <div className="start-stop-overlay">
          <button onClick={handleStop}>STOP</button><br/>
          <button onClick={handleStart}>START</button>
        </div>
      </main>
    </div>
  );
}

export default App;
