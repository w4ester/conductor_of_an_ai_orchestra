FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build the frontend
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy NGINX config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Expose web port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
