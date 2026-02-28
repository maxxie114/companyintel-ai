import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { ProgressMessage } from '../types';

interface LoadingProgressProps {
  sessionId: string;
  onComplete: (companyId: string) => void;
}

const STAGES = [
  { key: 'researching_company', label: 'Searching company info' },
  { key: 'analyzing_competitors', label: 'Analyzing competitors' },
  { key: 'gathering_financials', label: 'Gathering financial data' },
  { key: 'analyzing_team', label: 'Analyzing team & culture' },
  { key: 'processing_news', label: 'Processing news & sentiment' },
  { key: 'finalizing', label: 'Finalizing results' },
];

const LoadingProgress: React.FC<LoadingProgressProps> = ({
  sessionId,
  onComplete
}) => {
  const [progress, setProgress] = useState<ProgressMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [_companySlug, _setCompanySlug] = useState<string | null>(null);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsBase = apiUrl.replace(/^https:\/\//, 'wss://').replace(/^http:\/\//, 'ws://');
    const wsUrl = `${wsBase}/ws/progress/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data: ProgressMessage = JSON.parse(event.data);
      setProgress(data);

      if (data.type === 'completed') {
        // Extract company slug from the message or session
        // For now, we'll pass the session ID and let the backend handle it
        setTimeout(() => {
          onComplete(sessionId);
        }, 1000);
      }
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [sessionId, onComplete]);

  const currentProgress = progress?.progress || 0;
  const currentStage = progress?.stage || '';

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Analyzing Company...
      </Typography>

      <Box sx={{ mb: 3 }}>
        <LinearProgress
          variant="determinate"
          value={currentProgress * 100}
          sx={{ height: 10, borderRadius: 5 }}
        />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {Math.round(currentProgress * 100)}% complete
        </Typography>
      </Box>

      <List>
        {STAGES.map((stage, index) => {
          const stageProgress = index / STAGES.length;
          const isComplete = currentProgress > stageProgress;
          const isCurrent = stage.key === currentStage;

          return (
            <ListItem key={stage.key}>
              <ListItemIcon>
                {isComplete ? (
                  <CheckCircleIcon color="success" />
                ) : (
                  <HourglassEmptyIcon color={isCurrent ? 'primary' : 'disabled'} />
                )}
              </ListItemIcon>
              <ListItemText
                primary={stage.label}
                primaryTypographyProps={{
                  color: isComplete ? 'success.main' : isCurrent ? 'primary' : 'text.secondary'
                }}
              />
              {isCurrent && <Chip label="In Progress" size="small" color="primary" />}
            </ListItem>
          );
        })}
      </List>

      {!isConnected && (
        <Typography variant="body2" color="error" sx={{ mt: 2 }}>
          Connecting to server...
        </Typography>
      )}
    </Paper>
  );
};

export default LoadingProgress;
