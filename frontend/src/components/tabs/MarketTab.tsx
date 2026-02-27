import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  LinearProgress,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import { MarketIntelligence } from '../../types';

interface MarketTabProps {
  data: MarketIntelligence;
}

const MarketTab: React.FC<MarketTabProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Market Position
            </Typography>
            <Typography variant="body1">{data.market_position}</Typography>
            {data.market_share_percent && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Market Share: {data.market_share_percent}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={data.market_share_percent}
                  sx={{ mt: 1 }}
                />
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Niche
            </Typography>
            <Typography variant="body1">{data.niche}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Key Differentiators
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {data.differentiation.map((diff, index) => (
                <Chip key={index} label={diff} color="primary" />
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Target Markets
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {data.target_market.map((market, index) => (
                <Chip key={index} label={market} variant="outlined" />
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Competitors ({data.competitors.length})
            </Typography>
            <Grid container spacing={2}>
              {data.competitors.map((competitor, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="h6">{competitor.name}</Typography>
                        <Chip
                          label={`${competitor.market_overlap_percent}% overlap`}
                          size="small"
                          color="warning"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Relationship: {competitor.relationship}
                      </Typography>

                      <Box mt={2}>
                        <Typography variant="subtitle2" color="success.main">
                          Strengths:
                        </Typography>
                        <List dense>
                          {competitor.strengths.slice(0, 3).map((strength, i) => (
                            <ListItem key={i} sx={{ py: 0 }}>
                              <ListItemText
                                primary={`• ${strength}`}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>

                      <Box mt={1}>
                        <Typography variant="subtitle2" color="error.main">
                          Weaknesses:
                        </Typography>
                        <List dense>
                          {competitor.weaknesses.slice(0, 3).map((weakness, i) => (
                            <ListItem key={i} sx={{ py: 0 }}>
                              <ListItemText
                                primary={`• ${weakness}`}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default MarketTab;
