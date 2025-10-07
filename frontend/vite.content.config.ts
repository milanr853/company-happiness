// vite.content.config.ts: Dedicated build for the Content Script
import { defineConfig } from 'vite';
import { resolve } from 'path';
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    // Important: Use relative base path
    base: './',
    plugins: [tailwindcss()],

    // Plugins are not strictly necessary here, but can be added if needed
    // plugins: [], 

    build: {
        // Output to the same 'dist' directory as the main build
        outDir: 'dist',
        // Crucial: Do NOT empty the directory, or the popup build will be lost
        emptyOutDir: false,

        rollupOptions: {
            // ONLY specify the content script as the input
            input: {
                'content-script': resolve(__dirname, 'src/content-script.tsx'),
            },
            output: {
                // CRITICAL: Force the output format to IIFE for browser compatibility
                format: 'iife',

                // Ensure the content script file name is exactly 'content-script.js'
                entryFileNames: 'content-script.js',

                // Keep other assets bundled normally
                assetFileNames: 'assets/[name]-[hash].[ext]',
                chunkFileNames: 'assets/[name]-[hash].js',
            },
        },
    },
});
