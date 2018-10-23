#!/bin/bash  
img=$1

ssh 10.0.2.7 docker rmi -f ${img}
ssh 10.0.2.3 docker rmi -f ${img}
ssh 10.0.2.13 docker rmi -f ${img} 
ssh 10.0.2.5 docker rmi -f ${img}
