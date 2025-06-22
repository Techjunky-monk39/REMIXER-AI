# Simple React frontend Dockerfile
FROM node:20-alpine3.19 AS build
WORKDIR /app
COPY package.json ./
RUN apk update && apk upgrade --no-cache && npm install
COPY . .
RUN npm run build

FROM nginx:alpine
# Use custom nginx.conf to ensure port 8080 is used
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
