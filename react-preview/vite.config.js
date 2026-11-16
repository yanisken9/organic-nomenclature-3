import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: {
    // The native hosts resolve shared files at the repository root.
    // Keep React/Vite routes and generated /assets/ URLs on this server.
    proxy: Object.fromEntries([
      '/js/',
      '/css/',
      '/jsme/',
      '/scenarios/',
      '/mols/',
      '/spt/',
      '/react-preview/preserved-main-20261030/',
      '^/assets/namelecule-methane-v1\\.png(?:\\?|$)',
      '^/mulermoc-nom-52\\.html(?:\\?|$)',
      '^/design/(?:theory-library|welcome-proposal)\\.html(?:\\?|$)',
    ].map(path => [path, { target: 'http://127.0.0.1:8001' }])),
  },
  build: { outDir: 'dist', emptyOutDir: true },
});
