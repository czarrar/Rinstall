#!/usr/bin/env/Rscript

basedir <- getwd()
run <- function(cmd) {
    cat("RUNNING:", cmd, "\n")
    ret <- system(cmd)
    if (ret != 0) {
        cat("ERROR running", cmd, "exiting\n")
        quit(save="no", status=ret)
    }
    invisible(ret)
}

# Various Dependencies
cat("Installing various dependencies\n")
install.packages(
    c("foreach", "doMC", "multicore", "getopt", "optparse", 
        "bigmemory", "biganalytics", "bigmemory.sri")
, repos="http://cran.us.r-project.org")
install.packages(
    c("plyr", "Rcpp", "RcppArmadillo", "inline"), 
    dependencies=TRUE
, repos="http://cran.us.r-project.org")

# Install BigAlgebra
cat("\nInstalling bigalgebra\n")
run("svn checkout svn://svn.r-forge.r-project.org/svnroot/bigmemory/")
setwd("bigmemory/pkg")
run("R CMD INSTALL bigalgebra")
setwd(basedir)
run("rm -rf bigmemory")

# Installing niftir and friends
cat("\nInstalling connectir and friends\n")
run("git clonse https://github.com/czarrar/bigextensions.git")
setwd("bigextensions")
run("R CMD INSTALL bigextensions")
run("git clone https://github.com/czarrar/niftir.git")
setwd("niftir")
run("R CMD INSTALL niftir")
run("git clone https://github.com/czarrar/connectir.git")
setwd("connectir")
run("R CMD INSTALL connectir")
cat("\nCopying scripts for connectir\n")
bindir <- dirname(system("which R", intern=TRUE))
system(sprintf("cp connectir/inst/scripts/*.R %s/", bindir))
system(sprintf("rm -f %s/*_worker.R", bindir))
system(sprintf("chmod +x %s/*.R", bindir))
setwd(basedir)
run("rm -rf bigextensions niftir connectir")

# TODO: add copying of scripts to some bin location
