#!/usr/bin/env python

# AUTHOR: Zarrar Shehzad
# DATE: October, 26, 2012
# VERSION: 0.1


#############################
## Variables and Libraries ##
#############################

rbaseurl    = "http://cran.r-project.org/src/base/R-3"
blasurl     = "https://github.com/xianyi/OpenBLAS/zipball/master"
blasctlurl  = "http://prs.ism.ac.jp/~nakama/SurviveGotoBLAS2/blas_control_on_R/blasctl_0.2.tar.gz"

import os, shutil, urllib2, sys
from os import path
from subprocess import Popen, PIPE

def execute(command, error_message, capture_output=False):
    """Run command on command-line"""
    stdout = PIPE if capture_output else None
    
    print command
    p = Popen(command, shell=True, stdout=stdout)    
    (out,err) = p.communicate()
    
    if p.returncode != 0:
        raise SystemExit('\nERROR: %s' % error_message)
    
    return out

try:
    import mechanize
except ImportError:
    print '\nInstalling mechanize'
    execute("easy_install mechanize", "could not install mechanize")
    raise SystemExit('\nInstalled prerequisite software. Please rerun program.')


###############
## User Args ##
###############

import argparse
parser = argparse.ArgumentParser(description="""Install R with multi-threaded
                                    capabilities""")
parser.add_argument('-o', '--outdir', default='/usr', help="""In which 
                    directory should R be installed (default: %(default)s)""")
parser.add_argument('--r-opts', default=[], nargs='+', help="""Additional 
                    options to be used when running configure for R""")
parser.add_argument('-i', '--indir', default=None, help="""What is the path of 
                    the current R install? This option will then skip installing
                    R and also skips the use of -o and --r-opts options.""")

args = parser.parse_args()


#################
## Other Setup ##
#################

startdir = os.getcwd()
if os.getenv("PATH").find(path.join(args.outdir, "bin")) == -1:
    while True:
        msg = "%s is not in your path, would you like to add it [Y/n]?" % args.outdir
        add_to_path = raw_input(msg).lower()
        if add_to_path == '': add_to_path = 'y'
        if add_to_path in ['y', 'n']: break
else:
    add_to_path = 'n'


###############
## Install R ##
###############

if args.indir is None:
    args.indir = args.outdir

    print '\n============'
    print 'Installing R'
    
    # Get the url and filename to the latest version of R
    print '\nFetching download url'
    
    br = mechanize.Browser()
    br.open(rbaseurl)
    link = [ l for l in br.links(url_regex="R-") ][-1]
    link = link.absolute_url
    
    print '\nDownloading and Extracting'
    execute("wget -O r_latest.tar.gz %s" % link, "download failure")
    execute("tar -xzvf r_latest.tar.gz", "extraction failure")
    
    print '\nChanging Directories'
    tmp = execute('tar -tzf r_latest.tar.gz | head -n 1', \
                  'could not figure out directory name', \
                  capture_output=True)
    dirname = tmp.strip().strip('/$')
    os.chdir(dirname)
    
    print '\nCompiling and Installing'
    execute('./configure --prefix %s %s' % (args.outdir, " ".join(args.r_opts)), \
            'configure of R failed')
    execute('make', 'make of R failed')
    execute('make install', 'install of R failed')
    
    print '\nDone, removing source directory'
    os.chdir(startdir)
    shutil.rmtree(dirname)
    os.remove("r_latest.tar.gz")
    
    print '============\n'


######################
## Install OpenBlas ##
######################

print '\n==================='
print 'Installing OpenBlas'

print '\nDownloading and Extracting'
execute("wget --no-check-certificate -O openblas.zip %s" % blasurl, "download failure")
execute('unzip openblas.zip', "extraction failure")

print '\nChanging Directories'
tmp = execute("unzip -l openblas.zip | awk '{print $4}' | tail -n+5", \
        "could not figure out directory name", capture_output=True)
dirname = tmp.splitlines()[0].strip().strip('/$')
os.chdir(dirname)

print '\nCompiling'
execute('make', 'make of OpenBlas failed')

print '\nInstalling'
# archive default BLAS library but first check that required files exist
rdir1   = path.join(args.indir, 'lib64', 'R', 'lib')
rdir2   = path.join(args.indir, 'lib', 'R', 'lib')
rdir    = rdir1 if os.path.isdir(rdir1) else rdir2
if not path.exists(path.join(rdir, 'libRblas.so')):
    print "ERROR: Couldn't find the input %s. Make sure R is compiled so blas library is dynamically linked" % path.join(rdir, 'libRblas.so')
    sys.exit(1)
shutil.move(path.join(rdir,'libRblas.so'), path.join(rdir,'libRblas.so.keep'))
# copy over OpenBlas library
openblas_file = os.path.realpath(os.readlink('libopenblas.so'))
shutil.copy2(openblas_file, path.join(rdir, 'libRblas.so'))

print '\nDone, removing source directory'
os.chdir(startdir)
shutil.rmtree(dirname)
os.remove("openblas.zip")

print '===================\n'


######################
## Install BlasCtl ##
######################

print '\n============================'
print 'Installing R Package blasctl'

print '\nDownloading and Extracting'
execute("wget --no-check-certificate -O blasctl.tar.gz %s" % blasctlurl, "download failure")
execute("tar -xzvf blasctl.tar.gz", "extraction failure")

print '\nGetting Output Name'
tmp = execute('tar -tzf blasctl.tar.gz | head -n 1', \
              'could not figure out directory name', \
              capture_output=True)
dirname = tmp.strip().strip('/$')

print '\nInstalling'
r = path.join(args.outdir, 'bin', 'R')
execute("%s CMD INSTALL %s" % (r, dirname), "couldn't install R package")

print '\nDone, removing source directory'
os.chdir(startdir)
shutil.rmtree(dirname)
os.remove("blasctl.tar.gz")

print '============================\n'


###################
## Add R to path ##
###################

if add_to_path == 'y':
    print '\n====================='
    print 'Adding R to your path'
    
    fname = path.expanduser("~/.bashrc")
    f = open(fname, 'a')
    f.write("\nexport PATH=%s/bin:$PATH\n" % args.outdir)
    f.close()

    print '=====================\n'


print "ALL DONE!!!"
