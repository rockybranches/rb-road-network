#!/bin/bash
sudo kill -9 $(sudo ps -aux | grep justPop.exe | awk '{print $2}')
cp $RB_SRC/justPop.exe $RBP_SRC/resources/
cp $RB_SRC/justPop.exe $RB_WEB/resources/
jploc=$RB_WEB/resources/justPop.exe
sudo chown www-data:rocapp $jploc &&
    sudo chmod ug+rwx $jploc &&
    sudo chmod o+r $jploc &&
    sudo chmod o-w $jploc
