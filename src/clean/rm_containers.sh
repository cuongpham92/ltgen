
docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
ssh 10.0.2.3 docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
ssh 10.0.2.13 docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
ssh 10.0.2.5 docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
ssh 10.0.2.7 docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)

