import sys, os, time
#from utils import *
import shutil     
from run_blast_utils import * 
    

blast_rslt_dir = 'blast_rslts'
blast_working_dir = 'temp_blast'
commands = []
args = parse_args(sys.argv)


# If the -query_parallel arg is not specified, then just run program normally
commands = compile_cmd(args, blast_rslt_dir, blast_working_dir)

start_time = time.time()
exec_commands(commands)
shutil.rmtree(blast_working_dir)
print("---%s seconds ---" % (time.time() - start_time))
