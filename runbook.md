# Runbook

## Deploys

```
git pull
source tigerapps_env/bin/activate 
python manage.py collectstatic --noinput # deploy static content
sudo service supervisor restart # cycles the gunicorn server 
```

We have aggressive caching on tigerapps domain. Do a quick check to see if static files are wrong because of caching: compare the content at external URL http://wintersession.tigerapps.org/static/wintersession/files/main_style.css to `curl -H "Host:wintersession.tigerapps.org" localhost/static/wintersession/files/main_style.css`, for example. If they differ, purge cache in Cloudflare.

## Backups

```
mysqldump -u [user] -p [database] | gzip > [filename]
```

## Provisioning staff users

From Django's admin panel (e.g. at http://wintersession.tigerapps.org/djadmin/), create a User with Staff status and all permissions for the site of interest, e.g. Wintersession, only.

## apply a database migration
sudo /srv/tigerapps_env/bin/python manage.py schemamigration [app-name] --auto
/srv/tigerapps_env/bin/python manage.py migrate [app-name]

