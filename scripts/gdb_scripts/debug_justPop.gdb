set debuginfod enabled on

set args -f /home/robbiec/Git/rb-road-network/output/DiggsSouthSandResult.txt -t 4.50 --lat=36.0260084 --lon=-89.6864944 --radius=75000 --stride=0.009 --nthreads=2 --zoom=0.5

break justPop.cc:116

# breakpoint ahead of segfault
break justPop.cc:229
