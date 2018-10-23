#!/bin/bash

img=$1

#ssh 10.0.2.12 docker rmi smtp:v4
#ssh 10.0.2.13 docker rmi smtp:v4
#ssh 10.0.2.14 docker rmi smtp:v4
#ssh 10.0.2.15 docker rmi smtp:v4

scp ~/containers/${img} 10.0.2.7:~/containers
scp ~/containers/${img} 10.0.2.3:~/containers
scp ~/containers/${img} 10.0.2.13:~/containers
scp ~/containers/${img} 10.0.2.5:~/containers


ssh 10.0.2.7 docker load < /home/client/containers/${img}
ssh 10.0.2.3 docker load < /home/client/containers/${img}
ssh 10.0.2.13 docker load < /home/client/containers/${img}
ssh 10.0.2.5 docker load < /home/client/containers/${img}
