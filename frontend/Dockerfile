# Simple React frontend Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the frontend
RUN npm run build

# Serve with a lightweight web server
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

RUN sed -i 's/listen       80;/listen 8080;/' /etc/nginx/conf.d/default.conf
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
