./killproxy 
clear
cat ../logs/proxy.log 
rm -r ../logs/*
python2.7 proxy.py
