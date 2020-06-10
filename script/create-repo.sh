#!/bin/bash

mkdir temp
cd temp
rm -rf .* *.* *

git init
git commit -m "init empty" --allow-empty
echo a-1 >> readme.txt 
git add *
git commit -m "add a-1"

echo a-2 >> readme.txt 
git add *
git commit -m "add a-2"

echo a-3 >> readme.txt 
git add *
git commit -m "add a-3"

git log --oneline --all --graph

git checkout -b newone HEAD~2
git branch -a

sed -i '1s/^/b\-1\n/' readme.txt 
git add *
git commit -m "add b-1"

sed -i '1s/^/b\-2\n/' readme.txt 
git add *
git commit -m "add b-2"

sed -i '1s/^/b\-3\n/' readme.txt 
git add *
git commit -m "add b-2"

git log --oneline --all --graph
