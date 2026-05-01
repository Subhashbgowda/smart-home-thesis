import { useEffect, useState } from "react";
import {
    Box,
    Typography,
    Card,
    CardContent,
    Grid
} from "@mui/material";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    Legend
} from "recharts";

const BACKEND = "http://localhost:8000";

export default function Comparison() {
    const [data, setData] = useState<any[]>([]);

    async function load() {
        const res = await fetch(`${BACKEND}/api/compare`);
        const json = await res.json();

        setData([
            {
                name: "Rule-Based",
                avg_consumption: json.rule.avg_consumption,
                peak_consumption: json.rule.peak_consumption,
                avg_cost: json.rule.avg_cost,
            },
            {
                name: "ML-Based",
                avg_consumption: json.ml.avg_consumption,
                peak_consumption: json.ml.peak_consumption,
                avg_cost: json.ml.avg_cost,
            }
        ]);
    }

    useEffect(() => {
        load();
        const t = setInterval(load, 5000);
        return () => clearInterval(t);
    }, []);

    if (!data.length) {
        return <Typography>Loading comparison...</Typography>;
    }

    return (
        <Box p={3}>
            <Typography variant="h4" fontWeight={600} mb={3}>
                Rule vs ML Controller Comparison
            </Typography>

            <Grid container spacing={3}>
                {/* Average Consumption */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography fontWeight={600} mb={1}>
                                Average Consumption (kW)
                            </Typography>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="avg_consumption" fill="#2563eb" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Peak Consumption */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography fontWeight={600} mb={1}>
                                Peak Consumption (kW)
                            </Typography>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="peak_consumption" fill="#16a34a" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Average Cost */}
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography fontWeight={600} mb={1}>
                                Average Energy Cost (€)
                            </Typography>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="avg_cost" fill="#dc2626" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}
