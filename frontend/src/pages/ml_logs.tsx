// src/pages/MLLogs.tsx
import { useEffect, useRef, useState } from "react";
import {
    Box,
    Typography,
    TextField,
    MenuItem,
    Paper,
    Button,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

const BACKEND = "http://localhost:8000";

export default function MLLogs() {
    const [rows, setRows] = useState<any[]>([]);
    const [conditionFilter, setConditionFilter] = useState("all");
    const [occupancyFilter, setOccupancyFilter] = useState("all");
    const [priceFilter, setPriceFilter] = useState("all");
    const [limit, setLimit] = useState("all");

    const scrollRef = useRef<HTMLDivElement>(null);

    async function loadLogs() {
        const selectedLimit = limit === "all" ? 5000 : limit;
        const res = await fetch(`${BACKEND}/api/logs/ml?limit=${selectedLimit}`);
        const json = await res.json();
        const data = json.rows || [];

        const formatted = data.map((item: any, index: number) => ({
            seq: index + 1,
            id: item.timestamp,

            // ⭐ Beautiful human-readable timestamp
            timestampFull: new Date(item.timestamp).toLocaleString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: true,
            }),

            priceFormatted: Number(item.price_eur_per_kwh).toFixed(3),
            consumptionFormatted: Number(item.house_overall_kw).toFixed(2),
            ...item,
        }));

        setRows(formatted);
    }

    useEffect(() => {
        loadLogs();
        const t = setInterval(loadLogs, 2000);
        return () => clearInterval(t);
    }, [limit]);

    const filteredRows = rows.filter((row) => {
        if (conditionFilter !== "all" && row.condition !== conditionFilter)
            return false;
        if (occupancyFilter !== "all") {
            if (occupancyFilter === "1" && row.occupied !== true) return false;
            if (occupancyFilter === "0" && row.occupied !== false) return false;
        }
        if (priceFilter !== "all" && row.price_level !== priceFilter)
            return false;
        return true;
    });

    function jumpToLatest() {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }

    const columns = [
        { field: "seq", headerName: "#", width: 70 },

        {
            field: "timestampFull",
            headerName: "Timestamp",
            width: 230,
            cellClassName: "timestamp-cell",
        },

        { field: "priceFormatted", headerName: "Price", width: 120 },
        { field: "consumptionFormatted", headerName: "Consumption (kW)", width: 160 },
        { field: "temperature", headerName: "Temp (°C)", width: 110 },
        { field: "humidity", headerName: "Humidity", width: 110 },
        { field: "occupied", headerName: "Occupied", width: 120 },
        { field: "condition", headerName: "Condition", width: 130 },
        { field: "price_level", headerName: "Price Level", width: 130 },
        { field: "action", headerName: "Action", width: 240 },
        {
            field: "confidence",
            headerName: "Conf.",
            width: 100,
            valueFormatter: (params: any) =>
                (Number(params.value) * 100).toFixed(1) + "%",
        },
    ];

    return (
        <Box p={3}>
            <Typography variant="h4" fontWeight={600} mb={3}>
                ML Logs
            </Typography>

            {/* FILTER BAR */}
            <Paper
                sx={{
                    p: 2,
                    mb: 3,
                    display: "flex",
                    gap: 2,
                    flexWrap: "wrap",
                    background: "#f8f9fa",
                }}
            >
                <TextField
                    select
                    label="Condition"
                    value={conditionFilter}
                    onChange={(e) => setConditionFilter(e.target.value)}
                    sx={{ width: 180 }}
                >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="Clear">Clear</MenuItem>
                    <MenuItem value="Clouds">Clouds</MenuItem>
                    <MenuItem value="Rain">Rain</MenuItem>
                    <MenuItem value="Snow">Snow</MenuItem>
                </TextField>

                <TextField
                    select
                    label="Occupancy"
                    value={occupancyFilter}
                    onChange={(e) => setOccupancyFilter(e.target.value)}
                    sx={{ width: 180 }}
                >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="1">Occupied Only</MenuItem>
                    <MenuItem value="0">Empty Only</MenuItem>
                </TextField>

                <TextField
                    select
                    label="Price Level"
                    value={priceFilter}
                    onChange={(e) => setPriceFilter(e.target.value)}
                    sx={{ width: 180 }}
                >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                </TextField>

                <TextField
                    select
                    label="Show Entries"
                    value={limit}
                    onChange={(e) => setLimit(e.target.value)}
                    sx={{ width: 180 }}
                >
                    <MenuItem value="10">10</MenuItem>
                    <MenuItem value="25">25</MenuItem>
                    <MenuItem value="50">50</MenuItem>
                    <MenuItem value="100">100</MenuItem>
                    <MenuItem value="all">ALL</MenuItem>
                </TextField>

                <Button
                    variant="contained"
                    onClick={jumpToLatest}
                    sx={{ height: 55 }}
                >
                    Jump to Latest
                </Button>
            </Paper>

            {/* TABLE */}
            <Paper sx={{ height: 620, overflow: "auto" }} ref={scrollRef}>
                <DataGrid
                    rows={filteredRows}
                    columns={columns}
                    disableRowSelectionOnClick
                    sx={{
                        border: "none",
                        "& .MuiDataGrid-columnHeaders": {
                            background: "#111827",
                            color: "white",
                        },
                        "& .timestamp-cell": {
                            fontFamily: "monospace",
                            fontSize: "0.9rem",
                        },
                    }}
                    getRowHeight={() => 52}
                />
            </Paper>
        </Box>
    );
}
