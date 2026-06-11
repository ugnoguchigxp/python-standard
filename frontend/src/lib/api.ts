let accessToken: string | null = localStorage.getItem('access_token');

export const setAccessToken = (token: string | null) => {
  accessToken = token;
  if (token) {
    localStorage.setItem('access_token', token);
  } else {
    localStorage.removeItem('access_token');
  }
};

export const getAccessToken = () => accessToken;

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

export async function customFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = new Headers(options.headers || {});
  
  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  
  const config = {
    ...options,
    headers,
  };
  
  let response = await fetch(endpoint, config);
  
  const isAuthEndpoint = endpoint.includes('/auth/login') || 
                         endpoint.includes('/auth/register') ||
                         endpoint.includes('/auth/refresh');
                         
  if (response.status === 401 && !isAuthEndpoint) {
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refreshRes = await fetch('/api/auth/refresh', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });
        
        if (refreshRes.ok) {
          const data = await refreshRes.json();
          const newToken = data.access_token;
          setAccessToken(newToken);
          onRefreshed(newToken);
          isRefreshing = false;
          
          headers.set('Authorization', `Bearer ${newToken}`);
          return fetch(endpoint, { ...options, headers });
        } else {
          setAccessToken(null);
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
      } catch {
        setAccessToken(null);
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } finally {
        isRefreshing = false;
      }
    } else {
      return new Promise((resolve) => {
        subscribeTokenRefresh((token) => {
          headers.set('Authorization', `Bearer ${token}`);
          resolve(fetch(endpoint, { ...options, headers }));
        });
      });
    }
  }
  
  return response;
}

export const api = {
  get: async (url: string, options?: RequestInit) => {
    const res = await customFetch(url, { method: 'GET', ...options });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  },
  post: async (url: string, body?: any, options?: RequestInit) => {
    const res = await customFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  },
  put: async (url: string, body?: any, options?: RequestInit) => {
    const res = await customFetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  },
  delete: async (url: string, options?: RequestInit) => {
    const res = await customFetch(url, { method: 'DELETE', ...options });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  },
};
