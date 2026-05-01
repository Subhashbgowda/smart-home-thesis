import { useEffect, useRef, useState, useMemo } from "react";
import {
    Box,
    Typography,
    TextField,
    MenuItem,
    Paper,
    Button,
    FormGroup,
    FormControlLabel,
    Checkbox,
    Stack,
    useTheme,
} from "@mui/material";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

const BACKEND = "http://localhost:8000";

interface LogRow {
    id: string;
    seq: number;
    timestampFull: string;
    occupied?: boolean;
    overall_consumption: string;
    [key: string]: any;
}

export default function RuleLogs() {
    const theme = useTheme(); // detect light / dark mode

    const [rows, setRows] = useState<LogRow[]>([]);
    const [conditionFilter, setConditionFilter] = useState("all");
    const [occupancyFilter, setOccupancyFilter] = useState("all");
    const [limit, setLimit] = useState("all");

    const [columnVisibility, setColumnVisibility] =
        useState<Record<string, boolean> | null>(null);

    const scrollRef = useRef<HTMLDivElement>(null);
    const initializedColumns = useRef(false);

    // =====================================================
    //                    LOAD LOGS
    // =====================================================
    async function loadLogs() {
        try {
            const selected = limit === "all" ? 5000 : limit;
            const res = await fetch(`${BACKEND}/api/logs/rule?limit=${selected}`);
            const json = await res.json();
            const data = json.rows || [];

            const formatted: LogRow[] = data.map((item: any, index: number) => ({
                seq: index + 1,
                id: item.timestamp,
                timestampFull: new Date(item.timestamp).toLocaleString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true,
                }),
                overall_consumption: Number(item.house_overall_kw || 0).toFixed(2),
                ...item,
            }));

            setRows(formatted);

            if (!initializedColumns.current && formatted.length > 0) {
                const keys = Object.keys(formatted[0]);
                const vis: Record<string, boolean> = {};
                keys.forEach((k) => (vis[k] = true));
                vis["timestamp"] = false;

                setColumnVisibility(vis);
                initializedColumns.current = true;
            }
        } catch (err) {
            console.error("Error loading logs:", err);
        }
    }

    useEffect(() => {
        loadLogs();
        const t = setInterval(loadLogs, 2000);
        return () => clearInterval(t);
    }, [limit]);

    // =====================================================
    //                 FILTERED ROWS
    // =====================================================
    const filteredRows = useMemo(() => {
        return rows.filter((row) => {
            if (conditionFilter !== "all" && row.condition !== conditionFilter) return false;
            if (occupancyFilter === "1" && row.occupied !== true) return false;
            if (occupancyFilter === "0" && row.occupied !== false) return false;
            return true;
        });
    }, [rows, conditionFilter, occupancyFilter]);

    // =====================================================
    //                    SUMMARY PANEL
    // =====================================================
    const summary = useMemo(() => {
        if (filteredRows.length === 0) return null;
        const nums = filteredRows.map((r) => Number(r.overall_consumption) || 0);

        return {
            total: filteredRows.length,
            occupied: filteredRows.filter((r) => r.occupied === true).length,
            empty: filteredRows.filter((r) => r.occupied === false).length,
            avg: (nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(2),
            max: Math.max(...nums).toFixed(2),
        };
    }, [filteredRows]);

    // =====================================================
    //               CONDITIONAL ROW COLORS
    // =====================================================
    function getRowClass(params: any): string {
        const c = Number(params.row.overall_consumption);

        if (c > 3.5) return "row-high";
        if (c > 2.0) return "row-medium";

        if (params.row.occupied === true) return "row-occupied";
        if (params.row.occupied === false) return "row-empty";

        return "";
    }

    // =====================================================
    //                 COLUMN DEFINITIONS
    // =====================================================
    const baseColumns: GridColDef[] = [
        { field: "seq", headerName: "#", width: 60, cellClassName: "wrap-cell" },
        {
            field: "timestampFull",
            headerName: "Timestamp",
            width: 160,
            cellClassName: "timestamp-cell wrap-cell",
        },
    ];

    const dynamicFields = rows.length > 0 ? Object.keys(rows[0]) : [];
    const ignored = ["id", "seq", "timestampFull", "timestamp"];

    const dynamicColumns = dynamicFields
        .filter((f) => !ignored.includes(f))
        .map((f) => ({
            field: f,
            headerName:
                f === "overall_consumption"
                    ? "Overall Consumption (kW)"
                    : f.replace(/_/g, " ").toUpperCase(),
            width: 140,
            cellClassName: "wrap-cell",
        }));

    const allColumns = [...baseColumns, ...dynamicColumns];
    const visibleColumns =
        columnVisibility === null
            ? allColumns
            : allColumns.filter((c) => columnVisibility[c.field] !== false);

    // =====================================================
    //                    EXPORT
    // =====================================================
    function exportCSV() {
        const headers = visibleColumns.map((c) => c.headerName);
        const fields = visibleColumns.map((c) => c.field);

        const csvRows = [
            headers.join(","),
            ...filteredRows.map((row) =>
                fields.map((f) => JSON.stringify(row[f] ?? "")).join(",")
            ),
        ];

        saveAs(new Blob([csvRows.join("\n")], { type: "text/csv" }), "rule_logs.csv");
    }

    function exportExcel() {
        const fields = visibleColumns.map((c) => c.field);
        const exportData = filteredRows.map((row) => {
            const obj: Record<string, any> = {};
            fields.forEach((f) => (obj[f] = row[f]));
            return obj;
        });

        const ws = XLSX.utils.json_to_sheet(exportData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Logs");

        const buffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
        saveAs(
            new Blob([buffer], {
                type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }),
            "rule_logs.xlsx"
        );
    }

    // =====================================================
    //                    RENDER
    // =====================================================
    return (
        <Box p={3}>
            <Typography variant="h4" fontWeight={600} mb={2}>
                Rule-Based Logs
            </Typography>

            {/* SUMMARY */}
            {summary && (
                <Paper sx={{ p: 2, mb: 2 }}>
                    <Typography fontWeight={600}>Summary</Typography>
                    <Stack direction="row" spacing={4} mt={1}>
                        <div>Total: {summary.total}</div>
                        <div>Occupied: {summary.occupied}</div>
                        <div>Empty: {summary.empty}</div>
                        <div>Avg: {summary.avg} kW</div>
                        <div>Max: {summary.max} kW</div>
                    </Stack>
                </Paper>
            )}

            {/* FILTERS */}
            <Paper
                sx={{
                    p: 2,
                    mb: 3,
                    display: "flex",
                    gap: 2,
                    flexWrap: "wrap",
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
                    sx={{ height: 55 }}
                    onClick={() => {
                        if (scrollRef.current)
                            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
                    }}
                >
                    Jump to Latest
                </Button>
            </Paper>

            {/* COLUMN VISIBILITY */}
            {columnVisibility && (
                <Paper sx={{ p: 2, mb: 3 }}>
                    <Typography fontWeight={600} mb={1}>
                        Show / Hide Columns
                    </Typography>

                    <FormGroup sx={{ display: "flex", flexDirection: "row", flexWrap: "wrap" }}>
                        {Object.keys(columnVisibility)
                            .filter((c) => c !== "timestamp")
                            .map((col) => (
                                <FormControlLabel
                                    key={col}
                                    control={
                                        <Checkbox
                                            checked={columnVisibility[col]}
                                            onChange={() =>
                                                setColumnVisibility({
                                                    ...columnVisibility!,
                                                    [col]: !columnVisibility[col],
                                                })
                                            }
                                        />
                                    }
                                    label={col}
                                />
                            ))}
                    </FormGroup>
                </Paper>
            )}

            {/* EXPORT */}
            <Stack direction="row" spacing={2} mb={2}>
                <Button variant="outlined" onClick={exportCSV}>
                    Export CSV
                </Button>
                <Button variant="outlined" onClick={exportExcel}>
                    Export Excel
                </Button>
            </Stack>

            {/* ================= TABLE ================= */}
            <Paper sx={{ height: 620, overflow: "auto" }} ref={scrollRef}>
                <DataGrid
                    rows={filteredRows}
                    columns={visibleColumns}
                    disableRowSelectionOnClick
                    getRowClassName={getRowClass}
                    pageSizeOptions={[25, 50, 100]}
                    initialState={{
                        pagination: { paginationModel: { pageSize: 25, page: 0 } },
                    }}
                    sx={{
                        border: "none",

                        // HEADER COLORS (Dark + Light theme)
                        "& .MuiDataGrid-columnHeaders": {
                            background:
                                theme.palette.mode === "dark"
                                    ? "#0f172a"
                                    : "#111827",
                            color: "white",
                            whiteSpace: "normal !important",
                            lineHeight: "1.2 !important",
                        },

                        "& .MuiDataGrid-columnHeaderTitle": {
                            whiteSpace: "normal !important",
                            textOverflow: "clip !important",
                            overflow: "visible !important",
                        },

                        // MULTI-LINE CELL CONTENT
                        "& .wrap-cell": {
                            whiteSpace: "normal !important",
                            lineHeight: "1.2em !important",
                            wordBreak: "break-word",
                            paddingTop: "8px",
                            paddingBottom: "8px",
                        },

                        // CONDITIONAL COLORS
                        "& .row-high": { backgroundColor: "#ffebee !important" },
                        "& .row-medium": { backgroundColor: "#fff8e1 !important" },
                        "& .row-occupied": { backgroundColor: "#e8f5e9 !important" },
                        "& .row-empty": { backgroundColor: "#f3e5f5 !important" },

                        "& .timestamp-cell": {
                            fontFamily: "monospace",
                        },
                    }}
                    getRowHeight={(params) => {
                        return 60; // auto wrap height
                    }}
                />
            </Paper>
        </Box>
    );
}
