FROM nginx:1.19.0-alpine

# Remove the default config file and copy project config file
RUN rm /etc/nginx/conf.d/default.conf
COPY project_nginx.conf /etc/nginx/conf.d/nginx.conf

# Turn off the Nginx version display
COPY main_nginx.conf /etc/nginx/nginx.conf

# Install certbot for periodic renewal of SSL certificates
RUN curl https://dl.eff.org/certbot-auto -o /usr/local/bin/certbot-auto \
	&& chown root /usr/local/bin/certbot-auto \
	&& chmod 0755 /usr/local/bin/certbot-auto

# Install cerfication and other config files
COPY cert_ssl/ /etc/letsencrypt/live/flash-response.site/
COPY conf_ssl/ /etc/letsencrypt
