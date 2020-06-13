rm /rf temp
mkdir temp
cd temp


git init

git commit -m "init empty" --allow-empty

echo "1" >> readme.txt
git add readme.txt
git commit -m "add 1"

git checkout -b newone

echo "a" >> readme.txt
git add readme.txt
git commit -m "add a"

echo "b" >> readme.txt
git add readme.txt
git commit -m "add b"

git checkout master

echo "2" >> readme.txt
git add readme.txt
git commit -m "add 2"


