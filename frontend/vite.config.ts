import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path';

// This configuration is crucial for Chrome Extensions
export default defineConfig({
  // Use relative paths for assets inside the extension package
  base: './', 
  plugins: [react(), tailwindcss()],
  build: {
    // Output directory for the extension
    outDir: 'dist', 
    // Ensure that build does not rely on absolute paths
    emptyOutDir: true, 
    rollupOptions: {
      // Define entry points for the extension components
      input: {
        // 1. The main popup UI entry (index.html is the entry point for the popup)
        main: resolve(__dirname, 'index.html'), 
        // 2. The Content Script entry point (THIS IS THE FIX)
        'content-script': resolve(__dirname, 'src/content-script.tsx'), 
      },
      output: {
        // Ensure the content script output file name is exactly 'content-script.js'
        entryFileNames: (chunkInfo) => {
          // If the chunk is our content script, force the name to content-script.js 
          if (chunkInfo.name === 'content-script') {
            return '[name].js';
          }
          // Otherwise, use the standard assets path for other files
          return 'assets/[name].js';
        },
        chunkFileNames: `assets/[name].js`,
        assetFileNames: `assets/[name].[ext]`,
      },
    },
  },
});
