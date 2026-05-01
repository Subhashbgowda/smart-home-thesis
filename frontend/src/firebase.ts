// src/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyBBjN-4Em5nuuq86RCKim8KHtrWvql5dJw",
    authDomain: "smart-home-control-5f0d3.firebaseapp.com",
    databaseURL: "https://smart-home-control-5f0d3-default-rtdb.firebaseio.com",
    projectId: "smart-home-control-5f0d3",
    storageBucket: "smart-home-control-5f0d3.firebasestorage.app",
    messagingSenderId: "915670274779",
    appId: "1:915670274779:web:dcb792d8feaf70b594b2fe",
    measurementId: "G-29YTWY0E2C"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Authentication
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
