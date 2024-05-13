import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import LinearProgress from '@mui/material/LinearProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import { MuiFileInput } from "mui-file-input";

function ButtonGroup() {

    const [audioFile, setAudioFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(null);

    const [loaded, setLoaded] = useState(false);
    const [generated, setGenerated] = useState(false);

    const handleFileChange = (newAudioFile) => {
        setAudioFile(newAudioFile);
        setUploadProgress(0); // Reset progress when a new file is selected
        uploadFile(newAudioFile);
    };
  
    const uploadFile = (file) => {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);
  
        // Update progress
        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percentage = Math.round((event.loaded / event.total) * 100);
                setUploadProgress(percentage);
            }
        };
  
        xhr.open('POST', '/upload', true);
  
        xhr.onload = () => {
            if (xhr.status === 200) {
                alert('File uploaded successfully');
                setLoaded(true);
            } else {
                alert('Upload failed');
                setLoaded(false);
            }
        };
        xhr.onerror = () => alert('Upload error');
        xhr.send(formData);
    };

    const runTask = async () => {

        try {
            const response = await fetch("/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error("Network response was not ok.");
            }
            console.log("Completed.");
        } catch (error) {
            console.error("There was a problem with your fetch operation:", error);
        }

    };

    const startTask = () => {
        fetch('/start-task', {method: 'POST'})
            .then(response => response.json())
            .then(data => checkStatus(data.task_id));
    };
    
    const checkStatus = (taskId) => {
        setTimeout(function() {
            fetch(`/task-status/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.state === 'SUCCESS') {
                        // Handle success, display results
                        console.log(data.result);
                    } else if (data.state !== 'FAILURE') {
                        // Still pending, keep polling
                        checkStatus(taskId);
                    } else {
                        // Handle failure
                        console.error(data.status);
                    }
                });
        }, 2000); // Poll every 2 seconds
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
            </Grid>
            <Grid item md={4}>
                <Button 
                    disabled={!loaded}
                    variant="outlined" 
                    color="primary" 
                    onClick={runTask}
                    style={{ 
                        maxWidth: "165px", 
                        maxHeight: "56px", 
                        minWidth: "165px", 
                        minHeight: "56px",
                        display: "flex",
                        flexWrap: "wrap"
                    }}
                >
                    Start
                </Button>
            </Grid>
            <Grid item md={4}>
                <Button
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
                </Button>
            </Grid>
        </Grid>
    );
}

export default ButtonGroup;