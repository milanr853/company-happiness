    # Stage 1: Build Stage
    # Use a Node.js base image with common tools
    FROM node:21-slim AS build

    # Set the working directory
    WORKDIR /app

    # Copy package.json and package-lock.json and install dependencies
    # This layer is cached well since package files rarely change
    COPY package*.json ./
    RUN npm install

    # Copy all remaining source code
    COPY . .

    # Build the production extension bundle (output goes to /app/dist)
    # The 'run build' command relies on the configurations we debugged (vite.config.ts)
    RUN npm run build

    # --- Stage 2: Final Output ---
    # Since the final output is static content (the dist folder), 
    # we don't need a running environment for the extension itself.
    # The final 'deployment' is simply zipping this dist folder for the Chrome Web Store.

    # We can create a lightweight final image that just holds the build artifacts
    # (though typically for an extension, we just zip the build directory on the CI runner).
    
    # For GitOps/CI purposes, a clean build container is enough. 
    # The primary function here is ensuring the build step is isolated.
    

