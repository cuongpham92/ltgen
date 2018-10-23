#!/bin/bash

docker service rm http-intranet_agent
docker service rm http-livestr_agent
docker service rm imap_agent
docker service rm smtp_agent
docker service rm ftp_agent
