// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "../src/components/layout";
import MLLogs from "../src/pages/ml_logs";
import RuleLogs from "../src/pages/rule_logs";
import Charts from "./pages/charts";
import Settings from "../src/pages/settings";
import Dashboard from "../src/pages/dashboard";
import Login from "../src/pages/login";
import RequireAuth from "./components/RequireAuth";
import Comparison from "./pages/Comparison";


import { useState, useMemo } from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// ✨ Allowed themes
export type ThemeMode =
  | "light"
  | "dark"
  | "blue"
  | "green"
  | "cyberpunk"
  | "sunset";

function App() {
  const [themeMode, setThemeMode] = useState<ThemeMode>("light");

  const handleThemeChange = (mode: string) => {
    const allowed: ThemeMode[] = [
      "light",
      "dark",
      "blue",
      "green",
      "cyberpunk",
      "sunset",
    ];

    if (allowed.includes(mode as ThemeMode)) {
      setThemeMode(mode as ThemeMode);
    }
  };

  // THEME DEFINITIONS
  const theme = useMemo(() => {
    switch (themeMode) {
      case "dark":
        return createTheme({ palette: { mode: "dark" } });

      case "blue":
        return createTheme({
          palette: {
            mode: "light",
            primary: { main: "#1e3a8a" },
            background: { default: "#e0e7ff", paper: "#c7d2fe" },
          },
        });

      case "green":
        return createTheme({
          palette: {
            mode: "light",
            primary: { main: "#047857" },
            background: { default: "#d1fae5", paper: "#a7f3d0" },
          },
        });

      case "cyberpunk":
        return createTheme({
          palette: {
            mode: "dark",
            primary: { main: "#ff00ff" },
            background: { default: "#0a0014", paper: "#190027" },
          },
          typography: { fontFamily: "Orbitron, sans-serif" },
        });

      case "sunset":
        return createTheme({
          palette: {
            mode: "light",
            primary: { main: "#fb923c" },
            background: { default: "#fff1e6", paper: "#ffe4d4" },
          },
        });

      default:
        return createTheme({ palette: { mode: "light" } });
    }
  }, [themeMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <BrowserRouter>
        <Routes>
          {/* ---------- PUBLIC ROUTE (No Layout) ---------- */}
          <Route path="/login" element={<Login />} />

          {/* ---------- PROTECTED ROUTES (With Layout) ---------- */}
          <Route
            path="/"
            element={
              <RequireAuth>
                <Layout themeMode={themeMode} setThemeMode={setThemeMode} />
              </RequireAuth>
            }
          >
            {/* Default redirect */}
            <Route index element={<Navigate to="/dashboard" replace />} />

            {/* Protected pages */}
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="ml-logs" element={<MLLogs />} />
            <Route path="rule-logs" element={<RuleLogs />} />
            <Route path="charts" element={<Charts />} />
            <Route path="comparison" element={<Comparison />} />
            <Route
              path="settings"
              element={<Settings onThemeChange={handleThemeChange} />}
            />
          </Route>

          {/* ---------- NOT FOUND ---------- */}
          <Route
            path="*"
            element={<h2 style={{ padding: 20 }}>Page Not Found</h2>}
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
