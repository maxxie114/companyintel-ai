import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Rating
} from '@mui/material';
import { ProductsAPIs } from '../../types';

interface APIsTabProps {
  data: ProductsAPIs;
}

const APIsTab: React.FC<APIsTabProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Documentation Quality
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Rating value={data.documentation_quality} readOnly precision={0.5} />
              <Typography variant="body2" color="text.secondary">
                {data.documentation_quality.toFixed(1)} / 5.0
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              SDK Languages
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {data.sdk_languages.map((lang) => (
                <Chip key={lang} label={lang} size="small" color="primary" />
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Products ({data.products.length})
            </Typography>
            <Grid container spacing={2}>
              {data.products.map((product, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {product.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {product.description}
                    </Typography>
                    <Chip label={product.category} size="small" sx={{ mt: 1 }} />
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              API Endpoints ({data.apis.length})
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Method</TableCell>
                    <TableCell>Path</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Category</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.apis.slice(0, 10).map((api, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Chip label={api.method} size="small" color="primary" />
                      </TableCell>
                      <TableCell>
                        <code>{api.path}</code>
                      </TableCell>
                      <TableCell>{api.description}</TableCell>
                      <TableCell>{api.category}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {data.apis.length > 10 && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Showing 10 of {data.apis.length} endpoints
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Pricing Tiers
            </Typography>
            <Grid container spacing={2}>
              {data.pricing.map((tier, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="h6">{tier.name}</Typography>
                    <Typography variant="h5" color="primary" gutterBottom>
                      {tier.price}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {tier.target_audience}
                    </Typography>
                    <Box component="ul" sx={{ pl: 2 }}>
                      {tier.features.map((feature, i) => (
                        <Typography component="li" variant="body2" key={i}>
                          {feature}
                        </Typography>
                      ))}
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default APIsTab;
