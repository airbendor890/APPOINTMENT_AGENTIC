import axios from "axios";
const BASE_URL = "http://192.168.0.171:8000";

export const RegisterUser = async (data) => {

    try {
      const response = await axios.post(
        `${BASE_URL}/users/register`,
        data
      );

      return response.data;
    } catch (error) {
      console.error("Registration failed Error:", error);
      return null;

    }
  
};


export const  LoginUser = async (formData) => {

    try {
      const response = await axios.post(
        `${BASE_URL}/users/login`,
        formData
      );

      return response.data;
    } catch (error) {
      console.error("Login failed Error:", error);
      return null;

    }
  
};