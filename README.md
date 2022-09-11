# Market Basket Analysis App

A simple Flask app that serves a `plotly` network graph, heatmap, or table of association rules on user request. The association rules are calculated using [`mlxtend`](http://rasbt.github.io/mlxtend/).

The user will upload data in `.csv`, `.xls`, or `.xlsx` format. The data is expected to contain the columns `InvoiceNo`, `Description`, and `Quantity`. After uploading the data, the user will select the preferred metric for these plots such as 'confidence', 'lift', or 'leverage'.

## Running the app locally
Install [Docker](https://docs.docker.com/get-docker/) and [Docker compose](https://docs.docker.com/compose/install/). Compose version 2 is recommended. You can also run `./install_docker.sh`. Run the app locally with `docker compose up -d`. The app should be accessible on port 5000.

![landing](images/market-basket-app-landing.png)


## Docker Fargate Deployment

An ecs context must be created and used for deployments. Create an ecs context and switch to it with
```docker
docker context create myecscontext
docker context use myecscontext
```
Note that your `DOCKER_HOST` environment variable must be unset e.g. `unset DOCKER_HOST` or `docker context use` will not work.

You may get errors about ECS not supporting bind mounts from host. 

Launch the app with `docker compose -p my-app -f docker-compose.yml -f docker-compose.prod.yml up`. Note that if `-p` isn't specified, it will take the project name as the name of directory, which contains the illegal character `_`.  

An alternative to running `docker compose` is to use CloudFormation.
Create a CloudFormation template with `docker compose -f docker-compose.yml -f docker-compose.prod.yml convert > CloudFormation.yml`. Replace `_` with `-` everywhere in the template. 

Switch back to the default context with `docker context use default` and run 
```
aws cloudformation create-stack --stack-name <name> --template-body CloudFormation.yml --capabilities CAPABILITY_IAM
```
to create the infrastructure for the app. Note again that `--stack-name` cannot contain `_`.

### Port mappings
If you have port mappings such as `80:8080` or `443:8443` in your `docker-compose.yml` file, AWS will throw the error `published port can't be set to a distinct value than container port: incompatible attribute`. To work around this, use the solution posted [here](https://medium.com/tfogo/how-to-serve-your-website-on-port-80-or-443-using-aws-load-balancers-a3b84781d730).

## EC2 Deployment

### Cloning a repo to an EC2 instance
You will need to copy your public and private ssh keys to your instance. Follow the instructions [here](https://stackoverflow.com/questions/51380792/git-clone-ec2-instance-permissions-error). To clone a single branch, run `git clone -b <branch_name> --single-branch <git_repo_url>`

### Nginx config
Note that on a production server, please set `client_max_body_size 50M;` on your `nginx.conf`. Other things that may be worth tweaking are `proxy_read_timeout` and `proxy_connect_timeout`.

The `sqlite` database is stored in `/tmp` for now. Until a better place is found, the permissions for the db files here must be changed with `chmod 666 /tmp/prod.db`.

The `redis.conf` should be edited as follows: `daemonize yes` and `supervised no`. The `redis` server will start once the server is running.

Remember to create a `.env` file with the following attributes e.g.
```
DEV_DATABASE_URI=sqlite:///dev.db
PROD_DATABASE_URI=sqlite:///prod.db
FLASK_ENV=production
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

where the database string takes the form `dialect+driver://username:password@host:port/database`. The list of supported database drivers can be found [here](https://docs.sqlalchemy.org/en/14/dialects/index.html).

### SSL
Install `certbot` on your machine. Follow [these](https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/) instructions to obtain a certificate for nginx. To keep the certificates automatically renewed, set up a cron job:

```bash
crontab -e
```

When the editor opens, add the line `0 0 1 */2 * /usr/bin/letsencrypt renew >> /var/log/letsencrypt-renew.log`, which will renew the certificates every two months at 00:00 on the first day of the month.

For an AWS Fargate deployment, skip the cron job step. Copy the following files to your local machine:
```
/etc/letsencrypt/live/www.dealsinmyshop.ml/fullchain.pem
/etc/letsencrypt/live/www.dealsinmyshop.ml/privkey.pem 
/etc/letsencrypt/options-ssl-nginx.conf 
/etc/letsencrypt/ssl-dhparams.pem 
```

Make a directory e.g. `mkdir ~/my-letsencrypt && cd ~/my-letsencrypt`. Copy the files from letsencrypt into this directory with `sudo cp -r /etc/letsencrypt/archive/dealsinmyshop.ml .`.  Change the owner to `ubuntu` with `sudo chown -R ubuntu:ubuntu dealsinmyshop.ml/`. Go back to your local machine and copy the files with `scp -i ~/.ssh/my_pemfile.pem user@hostname:~/my-letsencrypt/dealsinmyshop.ml/* /path/to/local/`. Rename these files to remove the `1` suffix with `for f in *1.pem; do mv "$f" "$(echo "$f" | sed s/1//)"; done`.