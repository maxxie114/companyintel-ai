import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme, CssBaseline, Container, Box, Typography } from '@mui/material';
import CompanySearch from './components/CompanySearch';
import LoadingProgress from './components/LoadingProgress';
import Dashboard from './components/Dashboard';

const queryClient = new QueryClient();

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

type AppState = 'search' | 'loading' | 'dashboard';

function App() {
  const [state, setState] = useState<AppState>('search');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [companyId, setCompanyId] = useState<string | null>(null);

  const handleAnalysisStart = (newSessionId: string) => {
    setSessionId(newSessionId);
    setState('loading');
  };

  const handleAnalysisComplete = (newCompanyId: string) => {
    setCompanyId(newCompanyId);
    setState('dashboard');
  };

  const handleNewSearch = () => {
    setState('search');
    setSessionId(null);
    setCompanyId(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
          <Container maxWidth="xl">
            <Box sx={{ mb: 4, textAlign: 'center' }}>
              <Typography variant="h3" component="h1" gutterBottom>
                🚀 CompanyIntel
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Autonomous AI Company Intelligence Platform
              </Typography>
            </Box>

            {state === 'search' && (
              <CompanySearch onAnalysisStart={handleAnalysisStart} />
            )}
            {state === 'loading' && sessionId && (
              <LoadingProgress
                sessionId={sessionId}
                onComplete={handleAnalysisComplete}
              />
            )}
            {state === 'dashboard' && companyId && (
              <Dashboard
                companyId={companyId}
                onNewSearch={handleNewSearch}
              />
            )}
          </Container>
        </Box>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
