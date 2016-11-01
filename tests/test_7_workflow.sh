#!/usr/bin/env bash

./ditcmd list -c -v .

./ditcmd switchto t4

./ditcmd switchback

./ditcmd switchback

./ditcmd halt

./ditcmd resume

./ditcmd halt

./ditcmd append

./ditcmd switchto t1

./ditcmd switchback

./ditcmd resume

./ditcmd append

./ditcmd cancel

./ditcmd switchback

./ditcmd conclude

./ditcmd resume

./ditcmd conclude

./ditcmd resume

./ditcmd conclude

./ditcmd resume

./ditcmd conclude

./ditcmd resume

./ditcmd conclude

./ditcmd resume

./ditcmd conclude

./ditcmd resume

./ditcmd switchback

./ditcmd list -c -v .
