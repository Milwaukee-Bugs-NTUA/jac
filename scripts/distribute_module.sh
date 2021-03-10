#!/bin/bash

for i in 0 1 2 3
do
	rsync -av -e ssh --exclude='~/src/jacmodule/__pycache__' ~/src/ user@node$i:.
done
