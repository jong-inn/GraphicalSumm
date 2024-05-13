import React, { useEffect } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import draw from './Topic';

function Visualization() {

    useEffect(() => {
        // Call draw inside useEffect to ensure it's called after the component mounts
        draw();
    }, []);

    return (
        <Box sx={{ 
            display: "flex",
            flexWrap: "wrap",
            "& > :not(style)": {
                m: 1,
                width: 1200,
                height: 750
            },
        }}>
            <Paper elevation={3}>
                <Typography variant="h5" component="h5" align="center" sx={{ mt: 2, mb: 2, fontWeight: "bold" }}>
                    Visualization
                </Typography>
                <div 
                    id="container" 
                    style={{ 
                        overflowY: "auto",
                        maxHeight: 650,
                        align: "center",
                        overflowX: "hidden",
                    }}
                >
                </div>
            </Paper>
        </Box>
    );
}

export default Visualization;