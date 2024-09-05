# Build environment
FROM node:20.11.1-slim as build
WORKDIR /app
COPY package.json /app/
COPY package-lock.json /app/
RUN npm install
COPY . /app/
RUN npm run build

# Production environment
FROM nginx:alpine-slim
COPY --from=build /app/build /usr/share/nginx/html

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]