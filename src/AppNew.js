import React, { useState } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Stack from "@mui/material/Stack";
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
import Visualization from './Visualization';
import VisualizationOptions from './VisualizationOptions';
import PromptOptions from './PromptOptions';
import ButtonGroup from './ButtonGroup';
import axios from 'axios';


function App() {

    const [visOption, setVisOption] = useState("topic-clustering");

    const [transcriptPromptOpen, setTranscriptPromptOpen] = useState(false);
    const [transcriptPrompt, setTranscriptPrompt] = useState("");
    const [newTranscriptPrompt, setNewTranscriptPrompt] = useState("");
    const [data, setData] = useState(null);

    // Visualization Options
    const handleVisOptions = (event) => {
        setVisOption(event.target.value);
    };

    // Set Transcript Prompt Button
    const handleTranscriptPromptOpen = () => {
        setNewTranscriptPrompt(transcriptPrompt);
        setTranscriptPromptOpen(true);
    };

    const handleTranscriptPromptClose = () => {
        setNewTranscriptPrompt(transcriptPrompt);
        setTranscriptPromptOpen(false);
    };

    const handleTranscriptPromptRegister = () => {
        setTranscriptPrompt(newTranscriptPrompt);
        handleTranscriptPromptClose();
    };

    return (
        <Box
            id="mainBox"
            sx={(theme) => ({
                width: "100%",
                backgroundImage: "linear-gradient(180deg, #CEE5FD, #FFF)",
                backgroundSize: "100% 20%",
                backgroundRepeat: "no-repeat",
            })}
        >
            <Container
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    pt: { md: 3, sm: 12 },
                    pb: { md: 3, sm: 12 },
                }}
            >
                <Stack spacing={2} useFlexGap sx={{ width: { md: 1600 } }}>
                    <Grid container rowSpacing={1}>
                        <Grid item md={12}>
                            <Typography variant="h4" component="h1" align="left" sx={{ ml: 2, mb: 1, fontWeight: 'bold' }}>
                                GraphicalSumm
                            </Typography>
                        </Grid>
                        <Grid item md={12}>
                            <Typography variant="h6" component="h6" align="left" sx={{ ml: 2, mb: 1 }}>
                                A Visualization Summary of Meeting Notes
                            </Typography>
                        </Grid>
                    </Grid>
                    <Grid container columnSpacing={2}>
                        <Grid item md={8}>
                            <Visualization data={data} />
                        </Grid>
                        <Grid item md={4}>
                            <Grid container rowSpacing={0.5}>
                                <Grid item md={12}>
                                    <VisualizationOptions 
                                        radioValue={visOption}
                                        radioOnChange={handleVisOptions}
                                    />
                                </Grid>
                                <Grid item md={12}>
                                    <PromptOptions 
                                        transcriptPrompt={transcriptPrompt}
                                        newTranscriptPrompt={newTranscriptPrompt}
                                        setNewTranscriptPrompt={setNewTranscriptPrompt}
                                        transcriptPromptOpen={transcriptPromptOpen}
                                        handleTranscriptPromptOpen={handleTranscriptPromptOpen}
                                        handleTranscriptPromptClose={handleTranscriptPromptClose}
                                        handleTranscriptPromptRegister={handleTranscriptPromptRegister}
                                    />
                                </Grid>
                                <Grid item md={12} sx={{ ml:1, mt: 2 }}>
                                    <ButtonGroup transcriptPrompt={transcriptPrompt} setData={setData} />
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>
                </Stack>
            </Container>
        </Box>
    );
}

export default App;