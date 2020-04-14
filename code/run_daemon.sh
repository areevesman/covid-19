#!/usr/bin/env bash
conda activate covid19
cd /home/ec2-user/covid-19/code/
gunicorn --bind 0.0.0.0:8080 run_app -D