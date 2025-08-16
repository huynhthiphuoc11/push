/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  allowedDevOrigins: ['http://localhost:3000', 'http://172.20.10.2:3000'],
  async rewrites() {
    return [
      {
        source: '/candidates/:path*',
        destination: 'http://localhost:8000/candidates/:path*',
      },
      {
        source: '/jobs/:path*',
        destination: 'http://localhost:8000/jobs/:path*',
      },
      {
        source: '/search/:path*',
        destination: 'http://localhost:8000/search/:path*',
      },
      {
        source: '/rank/:path*',
        destination: 'http://localhost:8000/rank/:path*',
      },
      {
        source: '/analyze/:path*',
        destination: 'http://localhost:8000/analyze/:path*',
      },
    ];
  },
};

export default nextConfig;
