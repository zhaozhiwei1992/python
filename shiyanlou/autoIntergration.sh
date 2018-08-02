#!/bin/sh
GIT_DIR=/home/shiyanlou/Code/.git git pull
GIT_DIR=/home/shiyanlou/Code/.git git add .
GIT_DIR=/home/shiyanlou/Code/.git git commit -m "auto upload" .
GIT_DIR=/home/shiyanlou/Code/.git git push origin master
