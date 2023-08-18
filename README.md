This script allows you to analyze and plot the elution profile of your SEC-SAXS experiment using data from Subtracted .dat files in the  folder FOLDER/.
It creates two text files:
1- Ragtime_01.txt containing Index of the frame, I(0) and Rg values,

2- MW_02.txt containing Index of the frame, I(0) and MW1 values.

Then you can use software like Excel, Prism, SigmaPlot, etc., to plot the data as you want. 
You can also keep the graphs displayed by the script as a picture (see Output).

## User manual
# Prerequisites
   - Python 3.x
   - Necessary packages: numpy, matplotlib, scipy
   - SAXS Data need to be in Å-1 all sub file in one folder 

## Command syntax

 python Ragtime-vXX.py Folder qmin_offset qmax_offset

   - Folder/ : the name of the folder containing ONLY the Substrated files form SEC-SAXS.
   - `qmin_offset` : the offset (in number of lines) to be added to the first usable line to determine qmin, use the value from PRIMUS or RAW.
   - `qmax_offset`: the offset (in number of lines) to be added to the first usable line to determine qmax use the value from PRIMUS or RAW.

## Features
 1. Guinier approximation :
 - Read each .dat files and determine first usable line base on the provided qmin_offset qmax_offset.
 - Extraction of data for q and I(q) in the selected range.
 - Perform a linear regression to calculate Rg (radius of gyration) and I0 (intensity at q=0).
 - Write data to text file.
 - Display graph with I(0) and Rg vs Frame index

 2. Volume of correlation (VC):
 - Extract data up to q=0.3.
 - Calculate the integral of the product I(q)*q.
 - Calculation of VC, QR (quality factor) and MW (molecular weight).
 - Write data to text file.
 - Display graph with I(0) and MW vs Frame index
 
## Tests
 Works on mac M1 and Linux. It has been tested only on SEC-SAXS data from SWING beamline at Soleil-synchrotron France.
(but should work on different beamlines)
Jean-Marie Bourhis and Chat-GPT via mac-gpt (because I'm a "tanche" in python programming)

## Outputs 
1- I(0) and Rg vs Frames 
![Figure_1b](https://github.com/JMB-Scripts/SEC-SAXS-Analysis/assets/20182399/e59dee29-2056-4c30-874b-53c71f543d4e)

2- I(0) and MW vs Frames
![Figure_2b](https://github.com/JMB-Scripts/SEC-SAXS-Analysis/assets/20182399/a600f1aa-7606-473a-ab62-8f42a1238dc0)



