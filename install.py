#!/usr/bin/env python

rbaseurl    = "http://cran.r-project.org/src/base/R-2"
blasurl     = "https://github.com/xianyi/OpenBLAS/zipball/master"
blasctlurl  = "http://prs.ism.ac.jp/~nakama/SurviveGotoBLAS2/blas_control_on_R/blasctl_0.2.tar.gz"

import os, shutil, urllib2
from os import path
from subprocess import Popen, PIPE

import argparse
parser = argparse.ArgumentParser(description="""Install R with multi-threaded
                                    capabilities""")
parser.add_argument('-o', '--outdir', default='/usr', help="""In which 
                    directory should R be installed (default: %(default)s)""")
parser.add_argument('--r-opts', default=[], nargs='+', help="""Additional 
                    options to be used when running configure for R""")


args = parser.parse_args()
print args
raise SystemExit(1)

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

startdir = os.getcwd()


###############
## Install R ##
###############

print '\n============'
print 'Installing R'

# Get the url and filename to the latest version of R
print '\nFetching download url'

br = mechanize.Browser()
br.open(rbaseurl)
link = [ l for l in br.links(url_regex="R-") ][-1]

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
execute('./configure --prefix %s %s' % (args.outdir, " ".join(args.ropts)), \
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
execute("wget -O openblas.zip %s" % blasurl, "download failure")
execute('unzip openblas.zip', "extraction failure")

print '\nChanging Directories'
tmp = execute("unzip -l openblas.zip | awk '{print $4}' | tail -n+5", \
        "could not figure out directory name", capture_output=True)
dirname = tmp.splitlines()[0].strip().strip('/$')
os.chdir(dirname)

print '\nCompiling'
execute('make', 'make of OpenBlas failed')

print '\nInstalling'
# archive default BLAS library
rdir1   = path.join(args.outdir, 'lib64', 'R', 'lib')
rdir2   = path.join(args.outdir, 'lib', 'R', 'lib')
rdir    = rdir1 if os.path.isdir(rdir1) else rdir2
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
execute("wget -O blasctl.tar.gz %s" % blasctlurl, "download failure")
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
