#!/bin/bash

echo ""
ps auxf | grep 'R .* python3 runner.py .* -ct' -o
echo ""
echo ""

results_folder=$1

for game in kuhn leduc goofspiel random; do
	echo ""
	echo -e "\033[0;32m$game\033[0m"
	echo ""

	for filename in $results_folder/$game/*; do
		echo -e "\033[0;32m$filename\033[0m"
		n_prints=$(cat $filename | grep -o "duration\": [^,]*," | wc -l)
		n_it=$(cat $filename | grep -o "number_iterations\": [^,]*," | grep -o -E '[0-9]+')
		n_check=$(cat $filename | grep -o "check_every_iteration\": [^,]*," | grep -o -E '[-]? [0-9]+')
		tot_time=$(cat $filename | grep -o "total_duration\": [^,]*," | grep -o -E '[0-9]+(\.[0-9]+)?')
		if [[ $n_check > 0 ]]; then
			echo "$n_prints / $((n_it/n_check))        ($n_it iterations checking every $n_check)"
		fi
		if [ "$tot_time" != "" ]; then
			echo "Total duration: $tot_time seconds"
			m=$(bc -l <<< "$tot_time/60")
			echo "Total duration: $m minutes"
			h=$(bc -l <<< "$tot_time/3600")
			echo "Total duration: $h hours"
		fi
		echo ""
	done
done