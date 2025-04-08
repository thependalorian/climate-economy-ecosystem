/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  // Enable image optimization from remote sources
  images: {
    domains: ['images.unsplash.com', 'storage.googleapis.com', 'lh3.googleusercontent.com'],
  },
  // Configure webpack for compatibility
  webpack: (config) => {
    // Handle specific module issues if needed
    return config;
  },
}

module.exports = nextConfig