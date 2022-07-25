[program:portal_camerata]
user=alfonsogonzalez
directory=/home/alfonsogonzalez/portal_camerata
command=gunicorn -w 3 server:app
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/portal_camerata/portal_camerata.err.log
stdout_logfile=/var/log/portal_camerata/portal_camerata.out.log

