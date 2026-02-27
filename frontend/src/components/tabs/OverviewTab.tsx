import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Avatar
} from '@mui/material';
import { CompanyOverview } from '../../types';

interface OverviewTabProps {
  data: CompanyOverview;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Avatar
                src={data.logo_url}
                alt={data.name}
                sx={{ width: 80, height: 80 }}
              />
              <Box>
                <Typography variant="h5">{data.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {data.description}
                </Typography>
                <Box display="flex" gap={1} mt={1} flexWrap="wrap">
                  {data.industry.map((ind) => (
                    <Chip key={ind} label={ind} size="small" />
                  ))}
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Founded
            </Typography>
            <Typography variant="h6">{data.founded_year || 'N/A'}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Employees
            </Typography>
            <Typography variant="h6">{data.employee_count}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Headquarters
            </Typography>
            <Typography variant="h6">{data.headquarters}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              Status
            </Typography>
            <Chip
              label={data.status}
              color={data.status === 'public' ? 'success' : 'default'}
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Mission
            </Typography>
            <Typography variant="body1">{data.mission}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Website
            </Typography>
            <Typography variant="body1">
              <a href={data.website} target="_blank" rel="noopener noreferrer">
                {data.website}
              </a>
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default OverviewTab;
