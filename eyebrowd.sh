#!/bin/sh

BINFILE=$1
ps aux | grep `basename $BINFILE` | grep python | grep -v grep || $BINFILE
