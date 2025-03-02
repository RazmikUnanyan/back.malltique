server {
    listen ${LISTEN_PORT};
    server_name ec2-18-218-203-195.us-east-2.compute.amazonaws.com;
    return 301 https://$host$request_uri;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    500M;
    }
}