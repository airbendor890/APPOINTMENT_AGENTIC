import axios from "axios";
const BASE_URL = "http://192.168.0.171:8000";

const token = sessionStorage.getItem('token');

export const GetUpcomingAppointments = async () => {

    try {
      const response = await axios.get(`${BASE_URL}/appointments/me/upcoming`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error("Registration failed Error:", error);
      return null;

    }
  
};

export const GetPastAppointments = async () => {

    try {
      const response = await axios.get(`${BASE_URL}/appointments/me/past`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error("Registration failed Error:", error);
      return null;

    }
  
};