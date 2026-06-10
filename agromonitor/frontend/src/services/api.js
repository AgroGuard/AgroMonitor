const buildUrl = (path = '') => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return `http://127.0.0.1:8000${normalizedPath}`;
    }
  }

  return process.env.REACT_APP_API_URL || 'https://api.agromonitor.vercel.app' + normalizedPath;
};

export { buildUrl };
