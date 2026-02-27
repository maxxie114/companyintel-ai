import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Autocomplete
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { companyApi } from '../api/endpoints';

interface CompanySearchProps {
  onAnalysisStart: (sessionId: string) => void;
}

const DEMO_COMPANIES = [
  'Stripe', 'OpenAI', 'Anthropic', 'Yutori', 'Neo4j',
  'Render', 'Shopify', 'Twilio', 'Vercel', 'Supabase'
];

const CompanySearch: React.FC<CompanySearchProps> = ({ onAnalysisStart }) => {
  const [companyName, setCompanyName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim()) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await companyApi.analyze({
        company_name: companyName,
        options: {
          include_apis: true,
          include_financials: true,
          include_competitors: true,
          include_team: true,
          include_news: true,
          include_graph: true,
        },
      });

      onAnalysisStart(response.session_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start analysis');
      setIsAnalyzing(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom align="center">
        Analyze Any Company
      </Typography>
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
        Get comprehensive intelligence in 30 seconds
      </Typography>

      <Box component="form" onSubmit={handleSubmit}>
        <Autocomplete
          freeSolo
          options={DEMO_COMPANIES}
          value={companyName}
          onInputChange={(_, newValue) => setCompanyName(newValue)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Company Name"
              placeholder="e.g., Stripe, OpenAI, Shopify"
              fullWidth
              disabled={isAnalyzing}
            />
          )}
        />

        {error && (
          <Typography color="error" variant="body2" sx={{ mt: 1 }}>
            {error}
          </Typography>
        )}

        <Button
          type="submit"
          variant="contained"
          size="large"
          fullWidth
          startIcon={<SearchIcon />}
          disabled={isAnalyzing || !companyName.trim()}
          sx={{ mt: 2 }}
        >
          {isAnalyzing ? 'Starting Analysis...' : 'Analyze Company'}
        </Button>
      </Box>
    </Paper>
  );
};

export default CompanySearch;
