import sys
import subprocess
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('../testmerge.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

# first master to newone
first="newtwo"
second="newone"
MAX_COMMIT_LEN = 10000
MAX_CONFLICT = 500
ALLOW_AUTO_ADD = True
kerr = None
logger.info("python version {}".format(sys.version_info[0]))

class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != '\n':
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        self.level(sys.stderr)

def run_cmd_get_output(cmd):
    returncode = -1
    checkret = None
    checkerr = None
    if 0:
        ret = subprocess.run(cmd, shell=True, capture_output=True)
        checkret=ret.stdout.decode('utf8').strip()
        checkerr=ret.stderr.decode('utf8').strip()
        returncode = ret.returncode
    else:
        returncode = -1
        try:
            returncode = 0
            checkret = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
            if type(checkret) == type(b''):
                checkret = checkret.decode('utf8')
        except subprocess.CalledProcessError as e:
            # capture a error
            # File "/usr/lib/python3.4/subprocess.py", line 620, in check_output
            # raise CalledProcessError(retcode, process.args, output=output)
            # subprocess.CalledProcessError: Command '['lsx', '-l']' returned non-zero exit status 127
            logger.info(dir(e))
            returncode = e.returncode
            checkret = e.output
            checkerr = e.output
            kerr = e
    if checkret and type(checkret) ==type(b''):
        checkret = checkret.decode('utf8')
    if checkerr and type(checkerr) ==type(b''):
        checkerr = checkerr.decode('utf8')
    if checkret and type(checkret) != type(""):
        raise Exception("wrong type type:{} {}".format(type(checkret), repr(checkret)))
    return returncode, checkret, checkerr

def abort_cherry_pick():
    cmd = "git cherry-pick --abort"
    try:
        returncode,  checkout, checkerr = run_cmd_get_output(cmd)
    except:
        pass
        import traceback
        traceback.print_exc()

def has_cherry_hash(hash):
    cmd = "git log --grep {}".format(hash.strip())
    logger.debug(cmd)
    returncode, checkout, checkerr = run_cmd_get_output(cmd)
    logger.info("check_cherry_has is '{}'".format( checkout ))
    if returncode != 0:
        raise Exception("abnormal")
    if not checkout:
        result = False
    elif len(checkout) == 0 :
        result = False
    elif len(checkout) > MAX_COMMIT_LEN:
        raise Exception("wrong check_cherry_has return len(checkout) checkout:'{}'", len(checkout), checkout)
    else:
        result = True
    logger.info("checkout is type '{}''{}' '{}'".format( type(checkout) , len(checkout), checkout))
    logger.info("has_cherry_hash reult is {}".format(result))
   
    return result

sys.stdout = LoggerWriter(logger.debug)
sys.stderr = LoggerWriter(logger.warning)
cmd = "pwd"
returncode, checkret, checkerr = run_cmd_get_output(cmd)
logger.info("returncode is '{}' '{}'".format(returncode, checkret))

# find the merge-base of master and newone
cmd = "git merge-base {} {}".format(first, second)
logger.info(cmd)
returncode, checkret, checkerr = run_cmd_get_output(cmd)
hash=checkret.strip()
logger.info("hash={}".format(hash))
hash=hash.strip()
if len(hash) <10 and len(hash) != 40:
    raise Exception("not hash code")

cmd = "git checkout ".format(second)
returncode, checkret, checkerr = run_cmd_get_output(cmd)
checkret=checkret
logger.info("checkret is '{}'".format( checkret))
logger.info("hash is '{}'".format(hash))

# get the list of first's rev-list from hash to HEAD
cmd = "git rev-list --no-merges {}..{}".format(hash, first)
logger.info(cmd)
returncode, checkret, checkerr = run_cmd_get_output(cmd)
alist = checkret.split()
alist.reverse()
logger.info("alist is {}".format(len(alist)))
#logger.info(alist)

max_conflict = MAX_CONFLICT

count_all = len(alist)
count_contain = 0
count_empty = 0
count_success = 0
count_add = 0

count_conflict = 0
count_misc = 0
count_failed = 0


table_all = []
table_contain =[]
table_empty = []
table_success= []
table_add = []
table_conflict = []
table_misc = []

do_cherry_pick = True
if do_cherry_pick:
    if has_cherry_hash("12345678901234567890"):
        raise Exception("self-check has_cherry_hash failed !!!")
    for i in alist:
        count_failed = count_conflict + count_misc
        if max_conflict <= count_conflict or max_conflict <= count_failed:
            logger.info("max_conflict reach ! end it {} < {} or {}".format(max_conflict, count_conflict, count_failed))
            break
        # git cherry-pick
        has_pick = has_cherry_hash(i)
        if has_pick:
            # already merged
            count_contain += 1
            table_contain.append(i)
            logger.info("hash:count_contain had {}".format(i))
        else:
            # check curren status
            returncode, checkret, checkerr = None, None, None
            cmd = "git status"
            returncode, checkret, checkerr = run_cmd_get_output(cmd)
            if returncode != 0:
                logger.error("can not use git status")
                break
            if "cherry-picking" in checkret:
                abort_cherry_pick()
                logger.error("in a cherry-picking ! cannot do cherry-pick")
                break
            # start
            table_all.append(i)
            returncode = checkret = checkerr = None
            cmd = "git cat-file -p {} | grep '^parent '".format(i)
            returncode, checkret, checkerr = run_cmd_get_output(cmd)
            if returncode != 0 or len(checkret.split()) == 0:
                logger.error("cannot check a hashcode")
                break
            """ more then 2 parents are merged commit """
            is_merged_hash = False
            if (len(checkret.split())/2) > 1:
                is_merged_hash = True
                logger.debug("len is {}".format((len(checkret.split())/2)))
            logger.info("found is_merged_hash {}".format(is_merged_hash))
            if is_merged_hash:
                extra_parameter = "-m 1"
                logger.debug(checkret.split())
            else:
                extra_parameter = ""
            cmd = "git cherry-pick {} -x {}".format(extra_parameter, i)
            logger.info(cmd)
            returncode, checkret, checkerr = run_cmd_get_output(cmd)
            if returncode == 0:
                logger.info("hash:count_success complete cherry-pick '{}'".format(i))
                count_success += 1
                table_success.append(i)
            elif returncode != 0:
                # conflict
                logger.debug("returncode '{}', checkret '{}', checkerr '{}'".format(returncode, checkret, checkerr ))
            if returncode == 0:
                pass
            elif checkret and type(checkret) != type(""):
                logger.debug("cmd is '{}'".format(cmd))
                raise Exception("wrong type")
            elif checkret and "have unmerged files" in checkret or "after resolving" in checkret:
                cmd = "git diff --check"
                logger.info(cmd)
                returncode, checkret, checkerr = run_cmd_get_output(cmd)
                if returncode == 0 and len(checkret) == 0:
                    logger.info("no conflict diff")
                else:
                    logger.error("hash:count_conflict has conflict mark ! {}".format(i))
                    count_conflict += 1
                    table_conflict.append(i)
                    abort_cherry_pick()
                    # next hash
                    continue
                cmd = "git add *"
                logger.info(cmd)
                returncode, checkret, checkerr = run_cmd_get_output(cmd)
                logger.info("returncode {}".format(returncode))
                if returncode != 0:
                    logger.error("git add * => should success but failed ")
                    break
               
                cmd = "git commit --no-edit"
                logger.info(cmd)
                returncode, checkret, checkerr = run_cmd_get_output(cmd)
                logger.info("returncode {}".format(returncode))
                if returncode == 0:
                    # commit success ! it should have conflict !
                    if ALLOW_AUTO_ADD:
                        logger.error("hash:count_add add one ")
                        count_add +=1
                        table_add.append(i)
                        continue
                    else:
                        logger.error("hash: should not allow it ! {} ".format(i))
                        cmd = "git reset --hard HEAD~"
                        returncode, checkret, checkerr = run_cmd_get_output(cmd)
                        logger.error("reset git to HEAD~")
                        break                
                if checkret and "--allow-empty" in checkret:
                    # success. this is a empty merge. append it as a empty one
                    count_empty += 1
                    table_empty.append(i)
                    logger.error("hash:count_empty empty ! {}".format(i))
                else:
                    logger.error("hash:count_conflict unknown condition ! {}".format(i))
                    count_conflict += 1
                    table_conflict.append(i)
                abort_cherry_pick()
            elif checkerr and "--allow-empty" in checkerr:
                logger.info("has allow-empty! ignore-abort at '{}'".format(i))
                logger.info("hash:count_empty skip this one {}".format(i))
                count_empty += 1
                table_empty.append(i)
                abort_cherry_pick()
            else:
                logger.info("hash:count_misc unknow how to handle this one {}".format(i))
                abort_cherry_pick()
                count_misc += 1
                table_misc.append(i)
            if returncode != 0:
                logger.error("returncode not zero {}".format(returncode))
           

logger.info("last returncode is '{}'".format(returncode))
data = count_all, count_contain, count_empty,  count_success, count_add, "{0:.0%}".format((count_contain+count_empty+count_success+count_add)/(count_all))
logger.info("Result count_all {} count_contain{} count_empty {} count_success {} count_add {}=> complete {} ".format(*data))
data = count_failed, count_conflict, count_misc
logger.info("Result count_failed {} count_conflict {} count_misc {} ".format(*data))