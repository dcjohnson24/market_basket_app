FROM nginx:1.21.3

WORKDIR /app

RUN rm /etc/nginx/nginx.conf
COPY --chown=nginx:nginx nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
ARG project_conf
COPY --chown=nginx:nginx $project_conf /etc/nginx/conf.d/

RUN chown -R nginx:nginx /app && chmod -R 755 /app && \
        chown -R nginx:nginx /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chmod -R 755 /var/log/nginx; \
        chown -R nginx:nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid

USER nginx

