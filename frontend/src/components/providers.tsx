'use client';

import { SWRConfig } from 'swr';
import axios from 'axios';

// Default fetcher for SWR
const fetcher = async (url: string) => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
  
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  
  const response = await axios.get(fullUrl, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  
  return response.data;
};

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher,
        revalidateOnFocus: false,
        revalidateOnReconnect: true,
        shouldRetryOnError: false,
        dedupingInterval: 5000,
        errorRetryCount: 2,
        onError: (error) => {
          console.error('SWR Error:', error);
        },
      }}
    >
      {children}
    </SWRConfig>
  );
}
