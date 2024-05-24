cat dll_needs.txt | awk -F ' ' '{system("cp -v /usr/x86_64-w64-mingw32/bin/"$3" ./winbuild/")}'
