#!/bin/bash


pip install --upgrade pip

cat requirements.txt  | awk '{print "pip install " $0}' | bash