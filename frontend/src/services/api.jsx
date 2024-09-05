import axios from 'axios';
import { getToken, setToken } from '../utils/auth';
import { wait } from '../utils/timer';

const baseUrl = 'http://localhost:8000';

export const addCarDetails = async (plateNumber, ownerName, carModel, carColor) => {
    try{
      const token = getToken();
      const config = {
        headers: {
          Authorization: `Bearer ${token}`
        }
      };
      const response = await axios.post(`${baseUrl}/admin/add_car`, {
        plate_number: plateNumber,
        owner_name: ownerName,
        car_model: carModel,
        car_color: carColor
      }, config);
      return true;}
    catch(error){
      return false;
    }
};

export const fetchCarDetails = async () => {
      try {
        const token = getToken();
        const config = {
          headers: {
            Authorization: `Bearer ${token}`
          }
        };
        const response = await axios.get(`${baseUrl}/admin/car_details/all`, config);
        return response.data.data;
      } catch (error) {
        return error;
      }
};

export const deleteCar = async (plateNumber) => {
    try {
      const token = getToken();
      const config = {
        headers: {
          Authorization: `Bearer ${token}`
        }
      };
      await axios.delete(`${baseUrl}/admin/delete_car/${plateNumber}`, config);
      window.location.reload();
    } catch (error) {
      console.error(error);
    }
};

export const identifyCar = async (plateNumber) => {
  try{
    const token = getToken();
    const config = {
      headers: {
        Authorization: `Bearer ${token}`
      }
    };
    const response = await axios.get(`${baseUrl}/admin/car_details/${plateNumber}`, config);
    return response.data;
  } catch (error) {
      if (error.response && error.response.status === 404) {
        return false;
        // Create Car if not found.

        // await addCarDetails(plateNumber, "", "", "");
        // const token = getToken();
        // const config = {
        //   headers: {
        //     Authorization: `Bearer ${token}`
        //   }
        // };
        // const response = await axios.get(`${baseUrl}/admin/car_details/${plateNumber}`, config);
        // return response.data;
      }
  }
};

export const topUpBalance = async (topUpAmount, plateNumber) => {
    try {
      const token = getToken();
      const response = await fetch(`${baseUrl}/admin/transaction/ADMIN`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plate_number: plateNumber,
          amount: parseInt(topUpAmount)
        })
      });
      
      if (response.ok) {
        return true;
      } else {
        console.error('Failed to topup');
      }
    } catch (error) {
      console.error('Error:', error);
    }
};

export const toggleStolenStatus = async (plateNumber) => {
    try {
      const token = getToken();
      const response = await fetch(`${baseUrl}/admin/stolen/` + plateNumber, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          stolen: true
        })
      });

      if (response.ok) {
        return true;
      } else {
        console.error('Failed to toggle flag');
      }
    } catch (error) {
      console.error('Error:', error);
    }
};

export const toggleExemptedStatus = async (plateNumber) => {
    try {
      const token = getToken();
      const response = await fetch(`${baseUrl}/admin/exempted/` + plateNumber, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          exempted: true
        })
      });

      if (response.ok) {
        return true;
      } else {
        console.error('Failed to toggle flag');
      }
    } catch (error) {
      console.error('Error:', error);
    }
};

export const resetDB = async () => {
    try {
      const token = getToken();
      const response = await fetch(`${baseUrl}/admin/reset_db`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        window.location.href='/logout';
      } else {
        console.error('Failed to toggle flag');
      }
    } catch (error) {
      console.error('Error:', error);
    }
};

export const signUpAdmin = async (username, password) => {
    try {
      const response = await axios.post(`${baseUrl}/admin/add_user/`, {
        username,
        password
      });
      return true;
    } catch (error) {
      console.log("Couldn't Sign Up.")
    }
};

export const logInAdmin = async (username, password) => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    console.log("Sending req...");

    const config = {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    };

    const response = await axios.post(`${baseUrl}/token`, formData.toString(), config);
    const token = response.data.access_token;
    if (token) {
      localStorage.setItem('token', token);
      console.log("Set Token!");
      return true;
    } else {
      console.error("Token not received in the response.");
      return false;
    }
  } catch (error) {
    console.error("Login failed:", error);
    return false;
  }
}

export const updateCarDetails = async (plateNumber, ownerName, carModel, carColor) => {
    try {
      const token = getToken();
      const config = {
        headers: {
          Authorization: `Bearer ${token}`
        }
      };

      let url = `${baseUrl}/admin/update_car/${plateNumber}?`;

      if (ownerName) {
        url += `owner_name=${encodeURIComponent(ownerName)}&`;
      }

      if (carModel) {
        url += `car_model=${encodeURIComponent(carModel)}&`;
      }

      if (carColor) {
        url += `car_color=${encodeURIComponent(carColor)}&`;
      }

      if (url.endsWith('&')) {
        url = url.slice(0, -1);
      }

      const response = await axios.put(url, null, config);
      return true;
    } catch (error) {
      return false;
    }
};

export const fetchCarFromImage = async (base64Image) => {
    try{
      const token = getToken();
      const response = await fetch(`${baseUrl}/admin/anpr`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ image_data: base64Image }), // Send base64 encoded image data
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data from the server');
      }

      const data = await response.json();
      return data;}
    catch {
      return false;
    }
};

export const fetchCarHistory = async (plate_number) => {
    try{
      const token = getToken();
      const response = await fetch(`${baseUrl}/admin/car_history/${plate_number}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data from the server');
      }

      const data = await response.json();
      return data;}
    catch {
      return false;
    }
};