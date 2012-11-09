Rinstall
========

This program will only work on linux or mac. The main script install.py will download and install [R](http://cran.r-project.org) from source as well as download and install [OpenBlas](http://xianyi.github.com/OpenBLAS) from source. OpenBlas is an optimized BLAS library based on GotoBLAS2 that makes matrix operations in R run much faster and in parallel if you have a multicore system.

To install R linked to OpenBlas as well as a library that can control the number of cores used for linear algebra operations from within R, run the command below. *Note:* the following command will install R into /usr/lib and /usr/bin. To change the output path and/or set options to `./configure` see `install.py -h`.

```bash
./install.py    # make sure you are in the Rinstall directory
````

If you are then interested in making use of my connectir toolbox to conduct connectome-wide association studies, you can run the following command.

```bash
./connectir_install.R   # make sure you are in the Rinstall directory
```
