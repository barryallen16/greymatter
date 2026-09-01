# Static site: nginx alpine, < 10MB
FROM nginx:alpine

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy site (context is job-search dir itself)
COPY . /usr/share/nginx/html

# nginx alpine already exposes 80, healthcheck via wget
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://localhost/ || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
