FROM nginx:1.21.3

RUN rm /etc/nginx/nginx.conf
COPY --chown=nginx:nginx nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
ARG project_conf
COPY --chown=nginx:nginx ./conf/$project_conf /etc/nginx/conf.d/
COPY --chown=nginx:nginx ./conf/ /etc/letsencrypt/live/www.dealsinmyshop.ml/
COPY --chown=nginx:nginx ./conf/privkey.pem /etc/letsencrypt/
COPY --chown=nginx:nginx ./conf/ssl-dhparams.pem /etc/letsencrypt/
COPY --chown=nginx:nginx ./conf/options-ssl-nginx.conf /etc/letsencrypt/


RUN chown -R nginx:nginx /var/cache/nginx && \
        chmod -R 755 /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chmod -R 755 /var/log/nginx && \
        chown -R nginx:nginx /etc/nginx/conf.d && \
        chmod -R 755 /etc/nginx/conf.d

RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid

USER nginx


