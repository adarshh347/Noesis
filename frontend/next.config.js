/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Only use rewrites for local development
  // In production, the frontend calls the backend API directly via NEXT_PUBLIC_API_URL
  async rewrites() {
    // Skip rewrites in production - frontend calls backend API directly
    if (process.env.NODE_ENV === 'production') {
      return [];
    }
    // Local development: proxy API calls to local backend
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
}

module.exports = nextConfig
