import { auth, db } from "./firebase-config.js";
import { 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    onAuthStateChanged,
    signOut 
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { 
    doc, 
    setDoc, 
    getDoc 
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Signup Logic
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('regName').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const role = document.getElementById('regRole').value;

        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // Store user role in Firestore
            await setDoc(doc(db, "users", user.uid), {
                name: name,
                email: email,
                role: role,
                level: "Weak", // Default level for new students
                createdAt: new Date().toISOString()
            });

            alert("Account created successfully!");
            window.location.href = "dashboard.html";
        } catch (error) {
            console.error("Signup Error:", error.message);
            alert("Error: " + error.message);
        }
    });
}

// Login Logic
const authForm = document.getElementById('authForm');
const loginBtn = document.getElementById('loginBtn');
const loginError = document.getElementById('loginError');

if (authForm) {
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Reset UI state
        loginError.style.display = 'none';
        loginBtn.disabled = true;
        loginBtn.textContent = 'Authenticating...';

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            console.log("Auth success, fetching role...");

            // Fetch user role with a timeout/fallback
            try {
                const userDoc = await getDoc(doc(db, "users", user.uid));
                if (userDoc.exists()) {
                    const userData = userDoc.data();
                    if (userData.role === "teacher") {
                        window.location.replace("teacher-dashboard.html");
                    } else {
                        window.location.replace("dashboard.html");
                    }
                } else {
                    // Fallback if doc doesn't exist
                    console.warn("User document not found, defaulting to student dashboard.");
                    window.location.replace("dashboard.html");
                }
            } catch (firestoreError) {
                console.error("Firestore Error:", firestoreError);
                // Fallback redirect even on Firestore error
                window.location.replace("dashboard.html");
            }
        } catch (error) {
            console.error("Login Error:", error.code, error.message);
            loginBtn.disabled = false;
            loginBtn.textContent = 'Sign In';
            loginError.textContent = getFriendlyErrorMessage(error.code);
            loginError.style.display = 'block';
        }
    });
}

function getFriendlyErrorMessage(errorCode) {
    switch (errorCode) {
        case 'auth/invalid-credential':
            return 'Invalid email or password. Please try again.';
        case 'auth/user-not-found':
            return 'No account found with this email.';
        case 'auth/wrong-password':
            return 'Incorrect password.';
        case 'auth/too-many-requests':
            return 'Too many failed attempts. Please try again later.';
        default:
            return 'An error occurred during sign in. Please try again.';
    }
}

// Session Check
onAuthStateChanged(auth, async (user) => {
    const path = window.location.pathname;
    if (user) {
        if (path.includes("login.html") || path.includes("index.html")) {
            // Already logged in, redirect based on role
            try {
                const userDoc = await getDoc(doc(db, "users", user.uid));
                if (userDoc.exists()) {
                    const userData = userDoc.data();
                    if (userData.role === "teacher") {
                        window.location.replace("teacher-dashboard.html");
                    } else {
                        window.location.replace("dashboard.html");
                    }
                } else {
                    window.location.replace("dashboard.html");
                }
            } catch (error) {
                window.location.replace("dashboard.html");
            }
        }
    } else {
        // Not logged in, if on restricted pages, redirect to login
        if (path.includes("dashboard.html") || path.includes("quiz.html") || path.includes("teacher-dashboard.html")) {
            window.location.href = "login.html";
        }
    }
});
