### SEC-SAXS-Analysis

This script allows you to analyze and plot the elution profile of your SEC-SAXS experiment using already subtracted (.dat) files.
It creates two text files:

1- Ragtime_01.txt containing three columns: Index of the frame, I(0) and Rg values,

2- MW_02.txt containing three columns: Index of the frame, I(0) and MW values.

Then you can easily retrieve your region under your peak of interest.
You can use YOUR preferred software like Excel, Prism, SigmaPlot, etc., to plot the data as YOU want. 
If you want you can also keep the graphs displayed by the script as a picture (see Output).

### User manual
# Prerequisites
   - Python 3.x
   - Necessary packages: numpy, matplotlib, scipy
     
If needed just type in your terminal :
conda install numpy matplotlib scipy 
        
   - SAXS data need to be in Å-1.
   - All substracted files need to be in the same folder. 

## Command syntax
To launch the script in your terminal type:

 python Ragtime-v10.py Folder qmin_offset qmax_offset

   - Folder/ : the location of the folder containing ONLY the Substracted files from SEC-SAXS.
   - `qmin_offset`: the offset (in a number of lines) to determine qmin, use the value from PRIMUS (in the range box) or RAW (nmin) .
   - `qmax_offset`: the offset (in a number of lines) to determine qmax, use the value from PRIMUS (in the range box) or RAW (nmax).

## Features
 1. Guinier approximation :
 - Read each .dat files and determine the first usable line based on the provided qmin_offset qmax_offset.
 - Data extraction for q and I(q) in the selected range.
 - Perform a linear regression to calculate Rg (radius of gyration) and I(0) (intensity at q=0).
 - Write data to text file.
 - Display graph with I(0) and Rg vs Frame index

 2. Volume of correlation (VC):
 - Extract data up to q=0.3 or up to 8/Rg.
 - Calculate the integral of the product I(q)*q.
 - Calculation of VC, QR (quality factor) and MW (molecular weight).
 - Write data to a text file.
 - Display graph with I(0) and MW vs Frame index
 
## Tests
 Works on mac M1 and Linux. It has been tested only on SEC-SAXS data from SWING beamline at Soleil-synchrotron France.
(but should work with files from other SEC-SAXS beamlines)

## Graphical outputs 
1- I(0) and Rg vs Frames 

![Figure_1b](https://github.com/JMB-Scripts/SEC-SAXS-Analysis/assets/20182399/e59dee29-2056-4c30-874b-53c71f543d4e)

2- I(0) and MW vs Frames

![Figure_2b](https://github.com/JMB-Scripts/SEC-SAXS-Analysis/assets/20182399/a600f1aa-7606-473a-ab62-8f42a1238dc0)


Jean-Marie Bourhis and Chat-GPT via mac-gpt (because I'm a "tanche" in Python programming, but I'm hanging)

