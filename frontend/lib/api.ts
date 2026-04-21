// // lib/api.ts
// --------------------------Manual Axios with Refresh Logic (Old)--------------------------
// import axios from "axios";
// import { authClient } from "./auth-client";

// const api = axios.create({
//   baseURL: 'http://localhost:8000',
//   withCredentials: true,        // Important for httpOnly cookies
//   timeout: 10000,
// });

// // Flag to prevent infinite refresh loops
// let isRefreshing = false;

// // Request interceptor
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('access_token');
//   if (token && !config.url?.includes('/auth/refresh')) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

// // Response interceptor - Smart auto refresh
// api.interceptors.response.use(
//   (response) => response,
  
//   async (error) => {
//     const originalRequest = error.config;

//     // Prevent infinite loops
//     if (
//       error.response?.status === 401 &&
//       !originalRequest._retry &&
//       !originalRequest.url?.includes('/auth/refresh') &&   // Don't retry refresh itself
//       !isRefreshing
//     ) {
//       originalRequest._retry = true;
//       isRefreshing = true;

//       try {
//         const res = await axios.post(
//           'http://localhost:8000/auth/refresh',
//           {},
//           { withCredentials: true }
//         );

//         // Update token if using Bearer mode
//         if (res.data.access_token) {
//           localStorage.setItem('access_token', res.data.access_token);
//         }

//         isRefreshing = false;
//         return api(originalRequest); // Retry original request
//       } catch (refreshError) {
//         isRefreshing = false;
//         localStorage.removeItem('access_token');
        
//         // Only redirect if not already on login page
//         if (!window.location.pathname.includes('/login')) {
//           window.location.href = '/login';
//         }
//         return Promise.reject(refreshError);
//       }
//     }

//     // If it's a refresh error or any other error, just reject
//     return Promise.reject(error);
//   }
// );

// export default api;





//---------------- better auth ----------------------//

// lib/api.ts
import axios from "axios";
import { authClient } from "./auth-client";

const api = axios.create({
  baseURL: "http://localhost:8000",
  // withCredentials: true,
});

// Get fresh JWT from Better Auth before every request
api.interceptors.request.use(async (config) => {
  try {
    const { data } = await authClient.token(); // ← This gets the JWT
    if (data?.token) {
      config.headers.Authorization = `Bearer ${data.token}`;
    }
  } catch {
    // No token = guest request
  }
  return config;
});

// Keep your existing refresh logic (optional now)
// api.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     if (error.response?.status === 401) {
//       // Better Auth will handle session expiry automatically
//       window.location.href = "/login";
//     }
//     return Promise.reject(error);
//   }
// );

export default api;