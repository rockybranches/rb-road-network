#!/usr/bin/env bash
## set necessary environment variables to defaults (Linux)
echo "export -p RB_DATA=/home/${USER}/Documents/rb_data/" >> /home/${USER}/.bashrc
echo "export -p RB_WEB=/home/${USER}/public_html/rocky_branches/products/rbProducts/" >> /home/${USER}/.bashrc
echo "export -p RB_SRC=/home/${USER}/Git/rb-road-network/" >> /home/${USER}/.bashrc
source /home/${USER}/.bashrc
