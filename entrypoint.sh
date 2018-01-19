#!/bin/sh
/usr/local/src/mosquitto-1.4.13/initialConf.py
if [ $? -ne 0 ]; then
    echo "Error ocurred on initial mosquitto TLS setup"
    return -1
fi

python /var/www/app/KafkaMain.py &
/usr/local/sbin/mosquitto -c /usr/local/src/mosquitto-1.4.13/mosquitto.conf &
echo $! > /usr/local/src/mosquitto-1.4.13/mosquitto.pid
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
