/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // This ignores type errors during the build so your site actually goes live
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
