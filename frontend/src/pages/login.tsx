// src/pages/Login.tsx
import { useEffect } from "react";
import { auth, googleProvider } from "../firebase";
import { signInWithPopup } from "firebase/auth";
import { Button, Card, CardContent, Typography, Box } from "@mui/material";

export default function Login() {

    async function signInWithGoogle() {
        try {
            const result = await signInWithPopup(auth, googleProvider);
            const token = await result.user.getIdToken();

            // save token
            localStorage.setItem("authToken", token);

            // redirect to dashboard
            window.location.href = "/dashboard";
        } catch (err) {
            console.error(err);
        }
    }

    // already logged in?
    useEffect(() => {
        const token = localStorage.getItem("authToken");
        if (token) window.location.href = "/dashboard";
    }, []);

    return (
        <Box
            sx={{
                height: "100vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                background: "#eef2ff",
            }}
        >
            <Card sx={{ p: 3, width: 350, textAlign: "center" }}>
                <CardContent>
                    <Typography variant="h5" mb={2} fontWeight={600}>
                        Smart Home Login
                    </Typography>

                    <Button
                        variant="contained"
                        onClick={signInWithGoogle}
                        sx={{ width: "100%", mt: 2 }}
                    >
                        Sign in with Google
                    </Button>
                </CardContent>
            </Card>
        </Box>
    );
}
