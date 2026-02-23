set debuginfod enabled on

set args -f /home/robbiec/Git/rb-road-network/output/BattelleResults.txt \
    -t 4.50 \
    --lat=34.64944 \
    --lon=-85.56528 \
    --radius=75000 \
    --stride=0.009 \
    --nthreads=16 \
    --zoom=0.5
