import { apiClient } from './client';
import {
  AnalyzeRequest,
  AnalyzeResponse,
  CompanyResponse,
  GraphData
} from '../types';

export const companyApi = {
  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const { data } = await apiClient.post('/analyze', request);
    return data;
  },

  getCompany: async (companyId: string): Promise<CompanyResponse> => {
    const { data } = await apiClient.get(`/company/${companyId}`);
    return data;
  },

  getGraph: async (companyId: string, depth: number = 2): Promise<GraphData> => {
    const { data } = await apiClient.get(`/graph/${companyId}`, {
      params: { depth }
    });
    return data;
  },

  healthCheck: async () => {
    const { data } = await apiClient.get('/health');
    return data;
  }
};
