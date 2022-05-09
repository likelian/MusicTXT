#!/bin/bash

cd /var/www/private/
python3 MusicTXT.py
mv a.ly /var/www/html/download
cd /var/www/html/download
/usr/local/bin/lilypond a.ly
