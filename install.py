#!/usr/bin/env python

rbaseurl    = "http://cran.r-project.org/src/base/R-2"
blasurl     = "https://github.com/xianyi/OpenBLAS/zipball/master"
blasctlurl  = "http://prs.ism.ac.jp/~nakama/SurviveGotoBLAS2/blas_control_on_R/blasctl_0.2.tar.gz"
outdir      = "/usr"
ropts       = []

import os, shutil, urllib2
from functions import execute
from os import path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print '\nInstalling Beautiful Soup'
    execute("easy_install beautifulsoup4", "could not install html5lib")

startdir = os.getcwd()

###############
## Install R ##
###############

print '\n============'
print 'Installing R'

# Get the url and filename to the latest version of R
print '\nFetching download url'
f       = urllib2.urlopen(rbaseurl)
htmldoc = f.read()
soup    = BeautifulSoup(htmldoc)
links   = soup.find_all('a')
links   = [ l.get('href') for l in links if l.get('href')[0:2] == 'R-' ]
link    = "%s/%s" % (rbaseurl, links[-1])
f.close()

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
execute('./configure --prefix %s %s' % outdir, " ".join(ropts), \
        'configure of R failed')
execute('make', 'make of R failed')
execute('make install', 'install of R failed')

print '\nDone, removing source directory'
os.chdir(startdir)
shutil.rmtree(dirname)

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
rdir1   = path.join(outdir, 'lib64', 'R', 'lib')
rdir2   = path.join(outdir, 'lib', 'R', 'lib')
rdir    = rdir1 if os.path.isdir(rdir1) else rdir2
shutil.move(path.join(rdir,'libRblas.so'), path.join(rdir,'libRblas.so.keep'))
# copy over OpenBlas library
openblas_file = os.path.realpath(os.readlink('libopenblas.so'))
shutil.copy2(openblas_file, path.join(rdir, 'libRblas.so'))

print '\nDone, removing source directory'
os.chdir(startdir)
shutil.rmtree(dirname)

print '===================\n'


######################
## Install BlasCtl ##
######################

print '\n============================'
print 'Installing R Package blasctl'

print '\nDownloading and Extracting'
execute("wget -O blasct.tar.gz %s" % blascturl, "download failure")
execute("tar -xzvf blasct.tar.gz", "extraction failure")

print '\nGetting Output Name'
tmp = execute('tar -tzf blasct.tar.gz | head -n 1', \
              'could not figure out directory name', \
              capture_output=True)
dirname = tmp.strip().strip('/$')

print '\nInstalling'
r = path.join(outdir, 'bin', 'R')
execute("%s CMD INSTALL %s" % (r, dirname), "couldn't install R package")
