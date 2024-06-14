import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';

function VisualizationOptions({ radioValue, radioOnChange }) {
    return (
        <Box sx={{ 
            display: "flex",
            flexWrap: "wrap",
            "& > :not(style)": {
                m: 1,
                width: 600,
                height: 288
            },
        }}>
            <Paper elevation={3}>
                <Typography variant="h5" component="h5" align="center" sx={{ mt: 2, mb: 2, fontWeight: "bold" }}>
                    Visualization Options
                </Typography>
                <div style={{ marginLeft: "40px" }}>
                    <FormControl>
                        <RadioGroup
                            aria-labelledby="demo-radio-buttons-group-label"
                            name="radio-buttons-group"
                            value={radioValue}
                            onChange={radioOnChange}
                        >
                            <FormControlLabel value="topic-clustering" control={<Radio />} label="Topic Clustering" />
                            <FormControlLabel value="timeline" control={<Radio />} label="Timeline" />
                            {/* <FormControlLabel value="qna" control={<Radio />} label="Q & A" /> */}
                        </RadioGroup>
                    </FormControl>
                </div>
            </Paper>
        </Box>
    );
}

export default VisualizationOptions;