#! /bin/bash

while (($(df -h |grep -E " /$" | grep -E -o "([0-9]+%)" | grep -E -o "[0-9]+") < 90))
do
	python ssdb_test.py -q true -r 10000000 -n 5 -t "$(date -R)" -d ssdb_test
done
python echarts_data.py -d ssdb_test

