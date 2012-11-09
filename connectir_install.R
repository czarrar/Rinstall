#!/usr/bin/env Rscript --vanilla

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
        "bigmemory", "biganalytics")
)
install.packages(
    c("plyr", "Rcpp", "RcppArmadillo", "inline"), 
    dependencies=TRUE
)

# Install BigAlgebra
cat("\nInstalling bigalgebra\n")
run("svn checkout svn://scm.r-forge.r-project.org/svnroot/bigmemory")
setwd("bigmemory/pkg")
run("R CMD INSTALL bigalgebra")
setwd(basedir)
run("rm -r bigmemory")

# Installing niftir and friends
cat("\nInstalling connectir and friends\n")
run("svn checkout svn://scm.r-forge.r-project.org/svnroot/niftir")
setwd("niftir/pkg")
run("R CMD INSTALL bigextensions")
run("R CMD INSTALL niftir")
run("R CMD INSTALL connectir")
cat("\nCopying scripts for connectir\n")
bindir <- dirname(system("which R", intern=TRUE))
system(sprintf("cp connectir/inst/scripts/*.R %s/", bindir))
system(sprintf("chmod +x %s/*.R", bindir))
setwd(basedir)
run("rm -r niftir")

# TODO: add copying of scripts to some bin location