#!/bin/bash

for i in 0 1 2 3
do
	scp -r ~/src/ user@node$i:.
done
