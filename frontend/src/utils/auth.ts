// src/utils/auth.ts
import { auth } from "../firebase";

export function getCurrentUser() {
    const token = localStorage.getItem("authToken");
    if (!token) return null;

    const user = auth.currentUser;
    if (!user) return null;

    return {
        name: user.displayName || "User",
        email: user.email || "",
        photo: user.photoURL || ""
    };
}

export function logoutUser() {
    localStorage.removeItem("authToken");
    auth.signOut();
    window.location.href = "/login";
}
