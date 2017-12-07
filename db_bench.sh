#! /bin/bash
if [[ $# < 3 ]] ; then
	echo usage $0 "max_connections(max,start,step) record_num python_file params"
	exit 0
fi
type=$(echo $3|cut -d. -f 1)
out_dir=result_$type
rm -fr $out_dir
# exception, echo "-n",  print nothing, after $() -n lost
params=$(echo $*|sed -e 's/-n\s*[0-9]*/ /g'|cut -d\  -f 4-)
i=1
max=$(echo $1 | awk -F, '{print $1}')
start=$(echo $1 | awk -F, '{print $2}')
if [[ ! -z $start ]] ; then
    i=$start
fi
step=$(echo $1 | awk -F, '{print $3}')
while (( i <= $max ))
do
	python $3 $params -r $2 -n $i -d $out_dir
	if [[ $? != 0 ]] ; then
	    exit 1
	fi
    if [[ -z $step ]] ; then
        let i=i*2
    else
        let i=i+$step
    fi
done
python echarts_data.py -d $out_dir
cat $out_dir/benchmark.csv
