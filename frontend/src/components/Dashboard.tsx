import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Button,
  Chip,
  CircularProgress
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { companyApi } from '../api/endpoints';
import { CompanyResponse } from '../types';
import OverviewTab from './tabs/OverviewTab';
import APIsTab from './tabs/APIsTab';
import MarketTab from './tabs/MarketTab';

interface DashboardProps {
  companyId: string;
  onNewSearch: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ companyId, onNewSearch }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [companyData, setCompanyData] = useState<CompanyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Try to fetch with the companyId (could be session_id or slug)
        const data = await companyApi.getCompany(companyId);
        setCompanyData(data);
        setIsLoading(false);
      } catch (err: any) {
        // If 404, wait a bit and retry (data might still be processing)
        if (err.response?.status === 404) {
          setTimeout(async () => {
            try {
              const data = await companyApi.getCompany(companyId);
              setCompanyData(data);
              setIsLoading(false);
            } catch (retryErr: any) {
              setError('Company data not found. Please try analyzing again.');
              setIsLoading(false);
            }
          }, 2000);
        } else {
          setError(err.message || 'Failed to load company data');
          setIsLoading(false);
        }
      }
    };

    fetchData();
  }, [companyId]);

  // Poll for enrichment completion when background API analysis is still running
  useEffect(() => {
    if (!companyData || companyData.enrichment_status !== 'pending') return;

    const interval = setInterval(async () => {
      try {
        const updated = await companyApi.getCompany(companyId);
        if (updated.enrichment_status === 'completed') {
          setCompanyData(updated);
          clearInterval(interval);
        }
      } catch {
        // silently ignore poll errors
      }
    }, 30000); // poll every 30s

    return () => clearInterval(interval);
  }, [companyId, companyData?.enrichment_status]);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !companyData) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography color="error">{error || 'No data available'}</Typography>
        <Button onClick={onNewSearch} sx={{ mt: 2 }}>
          Try Another Company
        </Button>
      </Paper>
    );
  }

  const tabs = [
    { label: 'Overview', component: <OverviewTab data={companyData.data.overview} /> },
    { label: 'Products & APIs', component: <APIsTab data={companyData.data.products_apis} enrichmentStatus={companyData.enrichment_status} /> },
    { label: 'Market Intelligence', component: <MarketTab data={companyData.data.market_intelligence} /> },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4">{companyData.company_name}</Typography>
            <Box display="flex" gap={1} mt={1}>
              <Chip
                label={`Analyzed ${new Date(companyData.analyzed_at).toLocaleDateString()}`}
                size="small"
              />
              <Chip
                label={`Confidence: ${Math.round(companyData.metadata.confidence_score * 100)}%`}
                size="small"
                color="success"
              />
            </Box>
          </Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={onNewSearch}
          >
            New Search
          </Button>
        </Box>
      </Paper>

      <Paper elevation={2}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {tabs.map((tab, index) => (
            <Tab key={index} label={tab.label} />
          ))}
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabs[activeTab].component}
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;
