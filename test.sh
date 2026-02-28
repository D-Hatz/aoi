#!/bin/bash

NUM_REQUESTS=9
URL=$1

echo "Firing $NUM_REQUESTS requests to $URL..."

overall_start_time=$(date +%s)

for i in $(seq 1 "$NUM_REQUESTS"); do
    (
        start_time=$(date +%s)
        echo "Request $i start time: $start_time"

        curl -s "$URL"
        
        end_time=$(date +%s)
        echo "Request $i end time: $end_time"
    ) &
done

wait
