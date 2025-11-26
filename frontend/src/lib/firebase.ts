import { initializeApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBVjn_V4FGU0d3skMOWABFKhfsXg6UMPMk",
  authDomain: "resumax-66927.firebaseapp.com",
  projectId: "resumax-66927",
  storageBucket: "resumax-66927.firebasestorage.app",
  messagingSenderId: "93370291764",
  appId: "1:93370291764:web:e06cd09e58c87d5d7e1c61",
  measurementId: "G-8DQ8JS2R65"
};

// Initialize Firebase (only once)
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app;
