#!/bin/python
import subprocess

def abort_cherry_pick():
    cmd = "git cherry-pick --abort"
    ret = subprocess.run(cmd, shell=True, capture_output=True)
    hash=ret.stdout.decode('utf8').strip()

def has_cherry_hash(hash):
    cmd = "git log --grep {}".format(hash)
    ret = subprocess.run(cmd, shell=True, capture_output=True)
    checkret=ret.stdout.decode('utf8').strip()
    checkerr=ret.stderr.decode('utf8').strip()
    print("check_cherry_has is ", checkret)
    if ret.returncode != 0:
        raise Exception("abnormal")
    if len(checkret) + len(checkerr) == 0:
        result = False
    else:
        result = True
    print("has_cherry_hash reult is {}".format(result))
    return result


# first master to newone
first="master"
second="newone"

cmd = "pwd"
ret = subprocess.run(cmd, shell=True, capture_output=True)
print("ret is '{}'".format(ret))

# find the merge-base of master and newone
cmd = "git merge-base {} {}".format(first, second)
ret = subprocess.run(cmd, shell=True, capture_output=True)
hash=ret.stdout.decode('utf8').strip()
print("hash={}".format(hash))

cmd = "git checkout ".format(second)
ret = subprocess.run(cmd, shell=True, capture_output=True)
checkret=ret.stdout.decode('utf8').strip()
print("checkret is '{}'", checkret)

# get the list of first's rev-list from hash to HEAD
cmd = "git rev-list {}..{}".format(hash, first)
ret = subprocess.run(cmd, shell=True, capture_output=True)
alist = ret.stdout.decode('utf8').split()
print("alist is ")
print(alist)
alist.reverse()
print("alist is {}".format(len(alist)))
print(alist)
for i in alist:
    # git cherry-pick 
    has_pick = has_cherry_hash(i)
    if True != has_pick:
        cmd = "git cherry-pick -x {}".format(i)
        ret = subprocess.run(cmd, shell=True, capture_output=True)
        checkret = ret.stdout.decode('utf8').split()
        checkerr = ret.stderr.decode('utf8').split()
        print("alist is ")
        if 'Conflict' in checkret:
            print("has conflict ! stop at '{}'".format(i))
            print("please run abort")
            abort_cherry_pick()
            break
        elif "--allow-empty" in checkerr:
            print("has allow-empty! ignore-abort at '{}'".format(i))
            abort_cherry_pick()
            print("skip this one {}".format(i))
        elif ret.returncode != 0:
            print("returncode not zero {}".format(ret.returncode))
            abort_cherry_pick()
            break
        elif ret.returncode == 0:
            print("complete cherry-pick '{}'".format(i))


print("ret is '{}'".format(ret))
# git rev-list from output

