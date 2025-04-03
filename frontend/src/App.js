import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import SingleImageDetection from './components/SingleImageDetection';

// 创建主题
const theme = createTheme({
  palette: {
    primary: {
      main: '#0083B8',
    },
    secondary: {
      main: '#00A3E0',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static" color="primary" elevation={0}>
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                城市建筑物识别系统
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Container maxWidth={false} sx={{ mt: 4 }}>
            <Routes>
              <Route path="/" element={<SingleImageDetection />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;