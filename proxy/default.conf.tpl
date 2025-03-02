server {
    listen 80;
    server_name ec2-18-218-203-195.us-east-2.compute.amazonaws.com;
    return 301 https://$host$request_uri;
}

server {
    listen ${LISTEN_PORT};
    listen 443 ssl;
    server_name ec2-18-218-203-195.us-east-2.compute.amazonaws.com;

    ssl_certificate /etc/letsencrypt/live/${SERVER_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${SERVER_NAME}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    500M;
    }
}