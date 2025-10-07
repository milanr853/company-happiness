// Vite Configuration for Popup: company-happiness/frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import tailwindcss from '@tailwindcss/vite'

// This file only builds the standard POPUP UI (index.html)

export default defineConfig({
    base: './',
    plugins: [react(), tailwindcss()],

    build: {
        outDir: 'dist',
        emptyOutDir: true,

        rollupOptions: {
            input: {
                // ONLY the main popup entry remains here
                main: resolve(__dirname, 'index.html'),
            },
            // We can remove the output format/naming here since the single entry point 
            // no longer conflicts with the Content Script rules.
        },
    },
});
