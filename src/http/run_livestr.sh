#!/bin/bash

tapas_dir=${1}
livestr_link=${2}

python ${1}/play.py -u ${livestr_link} & sleep 30 ; kill $!
