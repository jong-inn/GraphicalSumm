import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Typography from '@mui/material/Typography';
import EditIcon from "@mui/icons-material/Edit";

function PromptOptions({ 
    transcriptPrompt, 
    newTranscriptPrompt, 
    setNewTranscriptPrompt,
    transcriptPromptOpen, 
    handleTranscriptPromptOpen, 
    handleTranscriptPromptClose, 
    handleTranscriptPromptRegister
}) {
    return (
        <Box sx={{ 
            display: "flex",
            flexWrap: "wrap",
            "& > :not(style)": {
                m: 1,
                width: 600,
                height: 360
            },
        }}>
            <Paper elevation={3}>
                <Typography variant="h5" component="h5" align="center" sx={{ mt: 2, fontWeight: "bold" }}>
                    Prompt Options
                </Typography>
                <Stack spacing={0.5} useFlexGap>
                    <Typography variant="subtitle1" align="left" sx={{ ml: 1, fontWeight: "bold" }}>
                        Transcript Prompt
                        <Button 
                            // size="small"
                            color="primary" 
                            onClick={handleTranscriptPromptOpen} 
                            sx={{ ml: -2 }}
                        >
                            <EditIcon />
                        </Button>
                        <Dialog 
                            open={transcriptPromptOpen} 
                            onClose={handleTranscriptPromptClose} 
                        >
                                <DialogContent
                                    sx={{ minWidth: 600, maxWidth: 600, minHeight: 100, maxHeight: 100 }}
                                >
                                    <TextField 
                                        id="transcript-prompt"
                                        required 
                                        autoFocus 
                                        margin="dense" 
                                        label="Transcript Prompt" 
                                        fullWidth 
                                        value={newTranscriptPrompt} 
                                        onChange={e => setNewTranscriptPrompt(e.target.value)} 
                                    />
                                </DialogContent>
                                <DialogActions>
                                    <Button onClick={handleTranscriptPromptClose} color="primary">Cancel</Button>
                                    <Button onClick={handleTranscriptPromptRegister} color="primary">Save</Button>
                                </DialogActions>
                        </Dialog>
                    </Typography>
                    <Box 
                        sx={{ 
                            ml: 1,
                            mr: 1,
                            border: 1, 
                            borderColor: "primary.main", 
                            borderRadius: 1, 
                            minHeight: 265, 
                            maxHeight: 265,
                            minWidth: 490,
                            maxWidth: 490
                        }}
                    >
                        <Typography sx={{ 
                            m: 1,
                            overflow: "hidden", 
                            textOverflow: "ellipsis", 
                            display: "-webkit-box",
                            WebkitLineClamp: "3",
                            wordBreak: "break-all",
                            WebkitBoxOrient: "vertical"
                        }}>
                            {transcriptPrompt}
                        </Typography>
                    </Box>
                </Stack>
            </Paper>
        </Box>
    );
}

export default PromptOptions;