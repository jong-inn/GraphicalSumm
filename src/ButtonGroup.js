import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import LinearProgress from '@mui/material/LinearProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import { MuiFileInput } from "mui-file-input";
import CircularProgress from '@mui/material/CircularProgress';
import axios from 'axios';

function ButtonGroup({ transcriptPrompt, setData }) {
    const [audioFile, setAudioFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(null);
    const [loaded, setLoaded] = useState(false);
    const [running, setRunning] = useState(false);
    const [generated, setGenerated] = useState(false);
    const [taskId, setTaskId] = useState(null);
    const [fileName, setFileName] = useState("");
    const [prompt, setPrompt] = useState(transcriptPrompt);
    const [statusMessage, setStatusMessage] = useState("");

    const handleFileChange = (newAudioFile) => {
        setAudioFile(newAudioFile);
        setFileName(newAudioFile.name);
        console.log(`audioFile name: ${newAudioFile.name}`);
        alert("File upload initiated");
        setUploadProgress(0); // Reset progress when a new file is selected
        uploadFile(newAudioFile);
        // alert("File upload completed");
    };

    const uploadFile = (file) => {
        const formData = new FormData();
        formData.append("file", file);
        
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:3005/upload", true);

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percentage = Math.round((event.loaded * 100) / event.total);
                setUploadProgress(percentage);
            }
        };

        xhr.onload = () => {
            if (xhr.status === 202) {
                // alert("File upload initiated");
                setLoaded(true);
            } else {
                alert("Upload failed");
                setLoaded(false);
            }
        };

        xhr.onerror = () => {
            console.error("Error uploading file");
            alert("Upload error");
            setLoaded(false);
        };

        xhr.send(formData);
        // alert("File upload completed");
    };

    const startTask = () => {
        setRunning(true);
        console.log(`audioFile name: ${fileName}`);
        fetch('http://localhost:3005/start-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fileName: fileName,
                prompt: prompt
            })
        })
        .then(response => response.json())
        .then(data => {
            setTaskId(data.task_id);
            console.log(`startTask: ${data.task_id}`);
            pollStatus(data.task_id);
        });
    };

    const pollStatus = (taskId) => {
        const interval = setInterval(() => {
            fetch(`http://localhost:3005/task-latest-message/${taskId}`)
                .then(response => {
                    console.log(`pollStatus, response status: ${response.status}`);
                    if (response.status === 404) {
                        // No messages yet, continue polling
                        return null;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.message) {
                        setStatusMessage(data.message);
                        if (data.message.includes("completed successfully") || data.message.includes("failed")) {
                            clearInterval(interval);
                            setRunning(false);
                            if (data.message.includes("completed successfully")) {
                                fetchJSONDictionary(taskId);
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error("Error fetching task status:", error);
                    clearInterval(interval);
                    setRunning(false);
                });
        }, 2000); // Poll every 2 seconds
    };

    const fetchJSONDictionary = (taskId) => {
        axios.get(`http://localhost:3005/get-js-file/${fileName}`)
            .then(response => {
                console.log(`fetchJSONDictionary: ${Object.keys(response.data.dictionary)}`);
                setData(response.data.dictionary);
                setGenerated(true);
            })
            .catch(error => {
                console.error("Error fetching JavaScript file:", error);
            });
    };

    return (
        <Grid container columnSpacing={0}>
            <Grid item md={4}>
                <MuiFileInput 
                    value={audioFile} 
                    placeholder="Upload File"
                    inputProps={{ accept: "audio/*, video/*" }} 
                    onChange={handleFileChange}
                    sx={{
                        maxWidth: "165px", 
                        maxHeight: "60px", 
                        minWidth: "165px", 
                        minHeight:"60px"
                    }}
                />
                {uploadProgress > 0 && (
                    <Box sx={{ width: "165px", mt: 1 }}>
                        <LinearProgress variant="determinate" value={uploadProgress} />
                        <Typography variant="body2" color="textSecondary">
                            {`${uploadProgress}%`}
                        </Typography>
                    </Box>
                )}
                {fileName && (
                    <Typography variant="body2" color="textSecondary">
                        {`Selected file: ${fileName}`}
                    </Typography>
                )}
            </Grid>
            <Grid item md={4}>
                <Button 
                    disabled={!loaded || running}
                    variant="outlined" 
                    color="primary" 
                    onClick={startTask}
                    style={{ 
                        maxWidth: "165px", 
                        maxHeight: "56px", 
                        minWidth: "165px", 
                        minHeight: "56px",
                        display: "flex",
                        flexWrap: "wrap"
                    }}
                >
                    {running ? <CircularProgress size={24} /> : "Start"}
                </Button>
                {statusMessage && (
                    <Typography variant="body2" color="textSecondary">
                        {statusMessage}
                    </Typography>
                )}
            </Grid>
            <Grid item md={4}>
                {/* <Button
                    disabled={!generated}
                    variant="outlined"
                    color="primary" 
                    style={{ 
                        maxWidth: "165px", 
                        maxHeight: "56px", 
                        minWidth: "165px", 
                        minHeight: "56px",
                        display: "flex",
                        flexWrap: "wrap"
                }}>
                    <RefreshIcon />
                </Button> */}
            </Grid>
        </Grid>
    );
}

export default ButtonGroup;