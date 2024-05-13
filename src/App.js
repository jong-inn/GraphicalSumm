import React, { useState } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import TextField from '@mui/material/TextField';
import RefreshIcon from '@mui/icons-material/Refresh';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import draw from './Topic';

function App() {
    return (
        <Grid container columnSpacing={2}>
            <Grid item md={8}>
                <Grid container rowSpacing={1}>
                    <Grid item md={10}>
                        <Typography variant="h4" component="h1" align="left" sx={{ mb: 3, fontWeight: 'bold' }}>
                            GraphicalSumm
                        </Typography>
                    </Grid>
                    <Grid item md={10}>
                        <Typography variant="h6" component="h6" align="left" sx={{ mb: 3 }}>
                            A Visualization Summary of Natural Language Contents
                        </Typography>
                    </Grid>
                    <Grid item md={12}>
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
                                <Typography variant="h5" component="h5" align="center" sx={{ mb: 3, fontWeight: "bold" }}>
                                    Visualization
                                </Typography>
                                <div align="center" id="container" style={{ overflowY: "auto"}}>
                                    {/* {draw()} */}
                                </div>
                            </Paper>
                        </Box>
                    </Grid>
                </Grid>
            </Grid>
            <Grid item md={4}>
                <Grid container rowSpacing={0.5}>
                    <Grid item md={12}>
                        <Box sx={{ 
                            display: "flex",
                            flexWrap: "wrap",
                            "& > :not(style)": {
                                m: 1,
                                width: 600,
                                height: 250
                            },
                        }}>
                            <Paper elevation={3}>
                                <Typography variant="h5" component="h5" align="center" sx={{ mb: 3, fontWeight: "bold" }}>
                                    Visualization Options
                                </Typography>
                                <div style={{ marginLeft: "40px" }}>
                                    <FormControl>
                                        {/* <FormLabel id="demo-radio-buttons-group-label">Gender</FormLabel> */}
                                        <RadioGroup
                                            aria-labelledby="demo-radio-buttons-group-label"
                                            defaultValue="topic-clustering"
                                            name="radio-buttons-group"
                                        >
                                            <FormControlLabel value="topic-clustering" control={<Radio />} label="Topic Clustering" />
                                            <FormControlLabel value="timeline" control={<Radio />} label="Timeline" />
                                            <FormControlLabel value="qna" control={<Radio />} label="Q & A" />
                                        </RadioGroup>
                                    </FormControl>
                                </div>
                            </Paper>
                        </Box>
                    </Grid>
                    <Grid item md={12}>
                        <Box sx={{ 
                            display: "flex",
                            flexWrap: "wrap",
                            "& > :not(style)": {
                                m: 1,
                                width: 600,
                                height: 250
                            },
                        }}>
                            <Paper elevation={3}>
                                <Typography variant="h5" component="h5" align="center" sx={{ mb: 3, fontWeight: "bold" }}>
                                    Prompt Options
                                </Typography>
                                <div style={{ marginLeft: "40px" }}>
                                    <FormControl>
                                        {/* <FormLabel id="demo-radio-buttons-group-label">Gender</FormLabel> */}
                                        <RadioGroup
                                            aria-labelledby="demo-radio-buttons-group-label"
                                            defaultValue="simple"
                                            name="radio-buttons-group"
                                        >
                                            <FormControlLabel value="simple" control={<Radio />} label="Simple Summary" />
                                            <FormControlLabel value="length-limit" control={<Radio />} label="Length Limit" />
                                            {/* <FormControlLabel value="qna" control={<Radio />} label="Q & A" /> */}
                                        </RadioGroup>
                                    </FormControl>
                                </div>
                            </Paper>
                        </Box>
                    </Grid>
                    <Grid item md={12}>
                        <Box sx={{ 
                            display: "flex",
                            flexWrap: "wrap",
                            "& > :not(style)": {
                                m: 1,
                                width: 600,
                                height: 250
                            },
                        }}>
                            <Paper elevation={3}>
                                <Typography variant="h5" component="h5" align="center" sx={{ mb: 3, fontWeight: "bold" }}>
                                    Evaluation Metrics
                                </Typography>
                                <div style={{ marginLeft: "40px" }}>
                                    Comming Soon...
                                </div>
                            </Paper>
                        </Box>
                    </Grid>
                    <Grid item md={12}>
                        <Grid container columnSpacing={1}>
                            <Grid item md={4}>
                                <Button 
                                    variant="outlined" 
                                    color="primary" 
                                    style={{ 
                                        maxWidth: "200px", 
                                        maxHeight: "60px", 
                                        minWidth: "200px", 
                                        minHeight:"60px",
                                        display: "flex",
                                        flexWrap: "wrap"
                                }}>
                                    File Upload
                                </Button>
                            </Grid>
                            <Grid item md={4}>
                                <Button 
                                    variant="outlined" 
                                    color="primary" 
                                    style={{ 
                                        maxWidth: "200px", 
                                        maxHeight: "60px", 
                                        minWidth: "200px", 
                                        minHeight:"60px",
                                        display: "flex",
                                        flexWrap: "wrap"
                                }}>
                                    Start
                                </Button>
                            </Grid>
                            <Grid item md={4}>
                                <Button
                                    variant="outlined"
                                    color="primary" 
                                    style={{ 
                                        maxWidth: "180px", 
                                        maxHeight: "60px", 
                                        minWidth: "180px", 
                                        minHeight:"60px",
                                        display: "flex",
                                        flexWrap: "wrap"
                                }}>
                                    <RefreshIcon />
                                </Button>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
}

export default App;