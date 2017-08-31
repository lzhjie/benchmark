#! /bin/bash
if [[ $# < 3 ]] ; then
	echo usage $0 max_connections record_num python_file params
	exit 0
fi
type=$(echo $3|cut -d. -f 1)
out_dir=result_$type
rm -fr $out_dir
# exception, echo "-n",  print nothing, after $() -n lost
params=$(echo $*|sed -e 's/-n\s*[0-9]*/ /g'|cut -d\  -f 4-)
i=1
end=$(echo $1 | cut -d, -f 2)
if [[ $end > 0 ]] ; then
    i=$(echo $1 | cut -d, -f 1)
else
    end=$1
fi
while (( i <= $end))
do
	python $3 $params -r $2 -n $i -d $out_dir
	if [[ $? != 0 ]] ; then
	    exit 1
	fi
	let i=i*2
done
python echarts_data.py -d $out_dir
cat $out_dir/benchmark.csv
