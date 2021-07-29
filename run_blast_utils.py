import sys, os, time
from subprocess import Popen, list2cmdline
import shutil
from progress.bar import Bar
    
    
def compile_cmd(args, blast_rslt_dir, blast_working_dir):
    """
    Compiles the dictionary of arguements into a list of arguements that can be run.
    
    :param args: A dictionary of command line arguements
    :param blast_rslt_dir: Path to the directory to store the results in
    :param blast_working_dir: Path to the temp directory to store fasta sequences
    :return: A list of command line arguements
    """
    commands = []
    cmd = []
    cmd += [args['script_args']['-program']]
    # Continue previous job?
    if '-continue' in args['script_args'].keys() and os.path.isdir(blast_working_dir):
        if not os.path.isdir(blast_rslt_dir):
            os.mkdir(blast_rslt_dir)
        ignored = set(('-out','-query'))
        # Compile the command line arguements to be run
        for key in args['blast_args'].keys():
            if not key in ignored and args['blast_args'][key] is not None:
                cmd += [key]
                cmd += [args['blast_args'][key]]
        # Now create a command for each fasta sequence
        for file in os.listdir(blast_working_dir):
            seq_cmd = cmd.copy()
            seq_cmd += ['-query']
            seq_cmd += [blast_working_dir + file]
            seq_cmd += ['-out']
            seq_cmd += [blast_rslt_dir + file.split('.')[0] \
                    + args['script_args']['rslt_ext']]
            commands += [seq_cmd]
    # If the -query_parallel arg is not specified, then just run program normally
    elif not '-query_parallel' in args['script_args'].keys():
        for key in args['blast_args'].keys():
            cmd += [key]
            if args['blast_args'][key] is not None:
                cmd += [args['blast_args'][key]]
        commands += [cmd]
    else:
        # Create files for fasta sequences.
        queries = parse_fasta(args['script_args']['-query_parallel'])
        if not os.path.isdir(blast_rslt_dir):
            os.mkdir(blast_rslt_dir)
        if not os.path.isdir(blast_working_dir):
            os.mkdir(blast_working_dir)
        write_queries(queries, blast_working_dir)
        ignored = set(('-out','-query'))
        # Compile the command line arguements to be run
        for key in args['blast_args'].keys():
            if not key in ignored and args['blast_args'][key] is not None:
                cmd += [key]
                cmd += [args['blast_args'][key]]
        # Now create a command for each fasta sequence
        for loc in queries.keys():
            seq_cmd = cmd.copy()
            seq_cmd += ['-query']
            seq_cmd += [blast_working_dir + loc + '.fasta']
            seq_cmd += ['-out']
            seq_cmd += [blast_rslt_dir + loc + args['script_args']['rslt_ext']]
            commands += [seq_cmd]
        
    return commands
    

def cpu_count():
    ''' Returns the number of CPUs in the system
    '''
    num = 1
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass

    return num
    

def exec_commands(cmds):
    ''' Exec commands in parallel in multiple process 
    (as much as we have CPU)
    '''
    if not cmds: return # empty list

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0
    def fail():
        sys.exit(1)
    print(cmds)
    print('-query_parallel' in cmds)

    max_task = cpu_count()
    processes = []
    with Bar('| BLASTing Sequences...', max=len(cmds)) as bar:
        while True:
            while cmds and len(processes) < max_task:
                task = cmds.pop()
                i = 0
                while i < len(task):
                    file = ""
                    if task[i] == '-query' and i < len(task) - 1:
                        file = task[i+1]
                        break
                    i += 1
                processes.append((Popen(task), file))

            for p in processes:
                if done(p[0]):
                    if success(p[0]):
                        if '-query_parallel' in cmds:
                            os.remove(p[1])
                        processes.remove(p)
                        bar.next()
                    else:
                        fail()

            if not processes and not cmds:
                break
            else:
                time.sleep(0.05)
            
    
def fix_win_filepath(filepath):
    """
    Replaces every '\' char with '\\'.
    
    :param filepath: The filepath to fix
    :return: String of a filepath with every '\' char replaced with '\\'.\
    """
    i = 0
    while filepath.find("\\") != -1:
        filepath = filepath.replace("\\", "/")
    while filepath.find("/") != -1:
        filepath = filepath.replace("/", "\\")
    return filepath
            
            
def parse_args(cmd_args):
    """
    Parses the command line arguments passed into the function.
    
    :param args: A list of command line arguments.
    :return: A dictionary of command line arguments.
    """
    args = {
                "blast_args"    : {},
                "script_args"   : {}
           }
    blast_single_args = set(('-h','-help','-version','-subject_besthit','-lcase_masking','-parse_deflines','-show_gis','-html','-ungapped','-remote','-use_sw_tback','-version'))   
    blast_double_args = set(('-import_search_strategy','-export_search_strategy','-task','-db','-dbsize','-gilist','-seqidlist','-negative_gilist','-negative_seqidlist','-taxids','-negative_taxids','-taxidlist','-negative_taxidlist','-ipglist','-negative_ipglist','-entrez_query','-db_soft_mask','-db_hard_mask','-subject','-subject_loc','-query','-out','-evalue','-word_size','-gapopen','-gapextend','-qcov_hsp_perc','-max_hsps','-xdrop_ungap','-xdrop_gap','-xdrop_gap_final','-searchsp','-seg','-soft_masking','-matrix','-threshold','-culling_limit','-best_hit_overhang','-best_hit_score_edge','-window_size','-query_loc','-query_loc','-outfmt','-num_descriptions','-num_alignments','-line_length','-sorthits','-sorthsps','-max_target_seqs','-num_threads','-mt_mode','-comp_based_stats'))
    script_args = set(("-program", "-query_parallel", '-continue'))
    
    i = 0
    while i < len(cmd_args):
        # Command line arguements specific to BLAST
        if cmd_args[i] in blast_single_args:
            args['blast_args'][cmd_args[i]] = None
        elif cmd_args[i] in blast_double_args:
            args['blast_args'][cmd_args[i]] = cmd_args[i+1]
            i += 1  
        elif cmd_args[i] == '-continue':
            args['script_args'][cmd_args[i]] = None
        elif cmd_args[i] in script_args:
            args['script_args'][cmd_args[i]] = cmd_args[i+1]
            i += 1  
        i += 1
    # Determine help specified
    if '-h' in args['blast_args'].keys():
        usage()
        if '-program' in args['script_args'].keys():
            Popen([args['script_args']['-program'], '-h'])
        exit()
    elif '-help' in args['blast_args'].keys():
        usage()
        if '-program' in args['script_args'].keys():
            Popen([args['script_args']['-program'], '-help'])
        exit()
        
    # fix filepaths if in windows
    if os.name == 'nt':
        for key in args['script_args'].keys():
            if args['script_args'][key] is not None:
                args['script_args'][key]  = fix_win_filepath(args['script_args'][key])
        for key in args['script_args'].keys():
            if args['script_args'][key] is not None:
                args['script_args'][key]  = fix_win_filepath(args['script_args'][key])
    # Determine file extension
    if '-outfmt' in args['blast_args'].keys():
        if args['blast_args']['-outfmt'] == '5':
            args['script_args']['rslt_ext'] = '.xml'
        elif '-html' in args['blast_args'].keys():
            args['script_args']['rslt_ext'] = '.xml'
        else:
            args['script_args']['rslt_ext'] = '.txt'
    else:
        args['script_args']['rslt_ext'] = '.txt'
        
    return args
    
    
def parse_fasta(filepath):
    """
    Parses a fasta file and extracts the sequence descriptions and sequences.
    
    :param filepath: The filepath of the file containing the multiple fasta sequences.
    :return: A dictionary mapping fasta descriptions to their sequences.
    """
    queries = {}
    f = open(filepath, 'r')
    content = f.read()
    f.close()
    content = content.split("\n")
    i = 0
    while i < len(content):
        if len(content[i].strip()) > 0:
            if content[i].strip()[0] == '>':
                des = content[i][1:].strip()
                queries[des] = content[i+1] 
                i += 1
        i += 1
    return queries  
         
            
def usage():
    msg = "\nThis program is basically a wrapper for the blastall program\n" 
    msg += "from NCBI. You can specify the blast program to run by including\n" 
    msg += "the argument [-progam blast_program]. All arguements that are\n"
    msg += "used in the blast program can also be passed into this script.\n" 
    msg += "This script also provide an additional option to blast multiple\n" 
    msg += "jobs in parallel. This can be done by specifying the\n"
    msg += "[-query_parallel query_file] option. This program will write the\n" 
    msg += "blast results to the folder 'blast_results', and the file for each\n"
    msg += "result will be saved by the fasta sequence description (what is\n"
    msg += "specified on the line after the '>' symbol). Please note the if\n" 
    msg += "duplicate fasta sequence descriptions exist, then they may override\n"
    msg += "each other."
    
    usage = "\tpy run_blast  "
    usage += "[-program blast_program] [-query_parallel query_file]\n"
    usage += "\t\t[-h] [-help] [-import_search_strategy filename]\n"
    usage += "\t\t[-export_search_strategy filename] [-task task_name] [-db database_name]\n"
    usage += "\t\t[-dbsize num_letters] [-gilist filename] [-seqidlist filename]\n"
    usage += "\t\t[-negative_gilist filename] [-negative_seqidlist filename]\n"
    usage += "\t\t[-taxids taxids] [-negative_taxids taxids] [-taxidlist filename]\n"
    usage += "\t\t[-negative_taxidlist filename] [-ipglist filename]\n"
    usage += "\t\t[-negative_ipglist filename] [-entrez_query entrez_query]\n"
    usage += "\t\t[-db_soft_mask filtering_algorithm] [-db_hard_mask filtering_algorithm]\n"
    usage += "\t\t[-subject subject_input_file] [-subject_loc range] [-query input_file]\n"
    usage += "\t\t[-out output_file] [-evalue evalue] [-word_size int_value]\n"
    usage += "\t\t[-gapopen open_penalty] [-gapextend extend_penalty]\n"
    usage += "\t\t[-qcov_hsp_perc float_value] [-max_hsps int_value]\n"
    usage += "\t\t[-xdrop_ungap float_value] [-xdrop_gap float_value]\n"
    usage += "\t\t[-xdrop_gap_final float_value] [-searchsp int_value] [-seg SEG_options]\n"
    usage += "\t\t[-soft_masking soft_masking] [-matrix matrix_name]\n"
    usage += "\t\t[-threshold float_value] [-culling_limit int_value]\n"
    usage += "\t\t[-best_hit_overhang float_value] [-best_hit_score_edge float_value]\n"
    usage += "\t\t[-subject_besthit] [-window_size int_value] [-lcase_masking]\n"
    usage += "\t\t[-query_loc range] [-parse_deflines] [-outfmt format] [-show_gis]\n"
    usage += "\t\t[-num_descriptions int_value] [-num_alignments int_value]\n"
    usage += "\t\t[-line_length line_length] [-html] [-sorthits sort_hits]\n"
    usage += "\t\t[-sorthsps sort_hsps] [-max_target_seqs num_sequences]\n"
    usage += "\t\t[-num_threads int_value] [-mt_mode int_value] [-ungapped] [-remote]\n"
    usage += "\t\t[-comp_based_stats compo] [-use_sw_tback] [-version]\n"
    
    print(msg)
    print("")
    print(usage)
    
    
def write_queries(queries, working_dir):
    """
    Writes a dictionary of fasta queries to file. 
    
    :param queries: Dictionary of fasta sequences to write.
    :param working_dir: Working directory to place fasta seqeunces to blast.
    """
    for key in queries.keys():
        f = open(working_dir+key+".fasta", 'w')
        f.write(">" + key + "\n" + queries[key])
        f.close()            
