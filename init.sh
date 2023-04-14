#!/bin/sh
sudo mysql < init.sql
mysql --user=spip --password=password spip < $(realpath "$1")
