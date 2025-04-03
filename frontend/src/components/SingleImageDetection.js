import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  Slider,
  Typography,
  Switch,
  FormControlLabel,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

// 自定义上传按钮样式
const VisuallyHiddenInput = styled('input')`
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  height: 1px;
  overflow: hidden;
  position: absolute;
  bottom: 0;
  left: 0;
  white-space: nowrap;
  width: 1px;
`;

const SingleImageDetection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [showLabel, setShowLabel] = useState(true);
  const [loading, setLoading] = useState(false);
  const [detectionResults, setDetectionResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDetectionResults(null);
      setError(null);
    }
  };

  const handleDetection = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://localhost:8000/detect/single', formData, {
        params: {
          confidence_threshold: confidenceThreshold,
          show_label: showLabel
        },
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setDetectionResults(response.data);
    } catch (err) {
      setError('检测过程中发生错误：' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        单张图片识别
      </Typography>

      <Grid container spacing={3}>
        {/* 左侧控制面板 */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              检测设置
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>置信度阈值</Typography>
              <Slider
                value={confidenceThreshold}
                onChange={(_, value) => setConfidenceThreshold(value)}
                min={0}
                max={1}
                step={0.01}
                valueLabelDisplay="auto"
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={showLabel}
                  onChange={(e) => setShowLabel(e.target.checked)}
                />
              }
              label="显示标签"
            />

            <Box sx={{ mt: 3 }}>
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                fullWidth
                sx={{ mb: 2 }}
              >
                选择图片
                <VisuallyHiddenInput type="file" onChange={handleFileSelect} accept="image/*" />
              </Button>

              <Button
                variant="contained"
                onClick={handleDetection}
                disabled={!selectedFile || loading}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : '开始识别'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* 中间预览区域 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              图片预览
            </Typography>
            <Box
              sx={{
                width: '100%',
                height: 400,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                backgroundColor: '#f5f5f5',
                borderRadius: 1
              }}
            >
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="预览图"
                  style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                />
              ) : (
                <Typography color="text.secondary">
                  请选择一张图片
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* 右侧结果区域 */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              检测结果
            </Typography>
            {error && (
              <Typography color="error" sx={{ mb: 2 }}>
                {error}
              </Typography>
            )}
            {detectionResults && (
              <Box>
                <Typography variant="body1" gutterBottom>
                  检测到 {detectionResults.data.total_objects} 个建筑物
                </Typography>
                {detectionResults.data.detections.map((detection, index) => (
                  <Paper key={index} sx={{ p: 1, mb: 1 }}>
                    <Typography variant="body2">
                      类型：{detection.class}
                    </Typography>
                    <Typography variant="body2">
                      置信度：{(detection.confidence * 100).toFixed(2)}%
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SingleImageDetection;