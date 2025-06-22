# Simple React frontend Dockerfile
FROM node:20-alpine3.19 AS build
WORKDIR /app
COPY package.json ./
RUN apk update && apk upgrade --no-cache && npm install
COPY . .
RUN npm run build

FROM nginx:alpine
# Change Nginx to listen on port 8080 for Cloud Run compatibility
RUN sed -i 's/listen       80;/listen 8080;/' /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
