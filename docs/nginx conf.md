server {
    listen 80;
    server_name 3.130.97.88 fadamasi-api.backyardsolutions.io;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Enable Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_vary on;

    # Redirect favicon.ico requests
    location = /favicon.ico { access_log off; log_not_found off; }

    # Serve static files
    location /static/ {
        alias /home/ubuntu/fadamasi_backend/assets/;
        autoindex off;  # Hide file listing for security
    }

    # Proxy requests to Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/fadamasi_backend.sock;

        # Ensure correct handling of large requests
        client_max_body_size 20M;
    }

    # Logging
    error_log /var/log/nginx/error.log;
    access_log /var/log/nginx/access.log;
}
