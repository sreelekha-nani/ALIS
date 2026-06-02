// Firebase CDN imports (browser-compatible, no bundler required)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Your web app's Firebase configuration (from Firebase Console)
const firebaseConfig = {
  apiKey: "AIzaSyABmTN2lOXNmrsDKfT2tFZsNhu9EC9IvkU",
  authDomain: "alis-system.firebaseapp.com",
  projectId: "alis-system",
  storageBucket: "alis-system.firebasestorage.app",
  messagingSenderId: "150522731240",
  appId: "1:150522731240:web:2764e76e429df13f9f075d",
  measurementId: "G-2RTM3PHXJS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };
