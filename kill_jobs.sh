#!/bin/bash
if [[ $0 != "-bash" ]] ; then
	echo usage: source $0
else
    jobs  -l |cut -d " "   -f 2 |xargs -I{} kill -9 {}
fi
