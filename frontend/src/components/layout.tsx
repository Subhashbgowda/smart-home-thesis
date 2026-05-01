// src/components/Layout.tsx
import {
    AppBar,
    Toolbar,
    Typography,
    Drawer,
    List,
    ListItemButton,
    ListItemText,
    Box,
    Switch,
    FormControlLabel
} from "@mui/material";
import { Link, Outlet } from "react-router-dom";
import { ThemeMode } from "../App";

const drawerWidth = 220;

interface LayoutProps {
    themeMode: ThemeMode;
    setThemeMode: (mode: ThemeMode) => void;
}

// Theme-based colors
const sidebarColors = {
    light: "#111827",
    dark: "#0f172a",
    blue: "#1e3a8a",
    green: "#065f46",
    cyberpunk: "#2d0036",
    sunset: "#b45309"
};

const appBarColors = {
    light: "#1f2937",
    dark: "#1e293b",
    blue: "#1e3a8a",
    green: "#047857",
    cyberpunk: "#ff00ff",
    sunset: "#fb923c"
};

export default function Layout({ themeMode, setThemeMode }: LayoutProps) {
    return (
        <Box sx={{ display: "flex", height: "100vh" }}>
            {/* Sidebar */}
            <Drawer
                variant="permanent"
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    [`& .MuiDrawer-paper`]: {
                        width: drawerWidth,
                        boxSizing: "border-box",
                        background: sidebarColors[themeMode],
                        color: "white",
                    },
                }}
            >
                <Toolbar />
                <List>
                    <ListItemButton component={Link} to="/dashboard">
                        <ListItemText primary="Dashboard" />
                    </ListItemButton>
                    <ListItemButton component={Link} to="/ml-logs">
                        <ListItemText primary="ML Logs" />
                    </ListItemButton>
                    <ListItemButton component={Link} to="/comparison">
                        <ListItemText primary="Comparison" />
                    </ListItemButton>
                    <ListItemButton component={Link} to="/rule-logs">
                        <ListItemText primary="Rule Logs" />
                    </ListItemButton>
                    <ListItemButton component={Link} to="/charts">
                        <ListItemText primary="Charts" />
                    </ListItemButton>
                    <ListItemButton component={Link} to="/settings">
                        <ListItemText primary="Settings" />
                    </ListItemButton>
                </List>
            </Drawer>

            {/* Top bar + content */}
            <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
                {/* AppBar */}
                <AppBar
                    position="fixed"
                    sx={{
                        zIndex: (theme) => theme.zIndex.drawer + 1,
                        marginLeft: `${drawerWidth}px`,
                        background: appBarColors[themeMode],
                    }}
                >
                    <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
                        <Typography variant="h6">Smart Home AI Dashboard</Typography>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={themeMode === "dark"}
                                    onChange={() =>
                                        setThemeMode(themeMode === "dark" ? "light" : "dark")
                                    }
                                />
                            }
                            label={themeMode === "dark" ? "Dark Mode" : "Light Mode"}
                        />
                    </Toolbar>
                </AppBar>

                {/* Main content */}
                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        overflowY: "auto",
                        p: 3,
                        marginTop: "64px",
                        bgcolor: themeMode === "dark" ? "#0f172a" : "#f3f4f6",
                        minHeight: "100vh",
                        transition: "0.3s ease",
                    }}
                >
                    {/* Nested pages render here */}
                    <Outlet />
                </Box>
            </Box>
        </Box>
    );
}
