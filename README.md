# Diffractometer Angles Finder
## Program under development for emulating Spec

## Requirements:

1. xrayutilities
2. numpy
3. scipy; version=1.4.1
4. pandas
5. tqdm

To start using DAF first you need to export the commands path, to do this enter in the clonned directory anda execute the init.sh script:

source init.sh

Now check if it went well by typing daf. and pressing tab two times, the result must be like that:

daf.amv     daf.expt    daf.mode    daf.rmap    daf.status  
daf.bounds  daf.init    daf.mv      daf.scan    daf.ub      
daf.cons    daf.macro   daf.reset   daf.setup   daf.wh 


Now you just need to move to a desired directory where you want the data to be generated and use DAF.

First initialize DAF:

daf.init -6c

All of the functions have a shell-like help option by typing -h or --help, like:

daf.expt -h

Them use the functions daf.expt, daf.mode, daf.bounds, daf.cons in order to define your experiment conditions.

To move use daf.amv for angle movement, daf.mv for hkl movement, daf.rmap to see a graphical of the reciprocal space, daf.scan to perform a scan.

A more consistent documentation is being developed.
