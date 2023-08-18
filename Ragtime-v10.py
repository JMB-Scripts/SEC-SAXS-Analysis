###################################################################
# This script allows you to analyze and plot the elution profile of
# your SEC-SAXS experiment using data from Subtracted files in the  folder FOLDER/.
# It creates two text files: Ragtime_01.txt containing Index of the frame, I(0) and Rg values,
# and MW_02.txt containing Index of the frame, I(0) and MW1 values.
# You can use software like Excel, Prism, SigmaPlot, etc., to plot the data as you wiwh. You can also keep the graphs display bys the script as a picture.
#
## User manual
# Prerequisites
#   - Python 3.x
#   - Necessary packages: numpy, matplotlib, scipy
#   - SAXS Data need to be in Å-1 all sub file in one folder 
#
## Command syntax
#
# python script.py Folder/ qmin_offset qmax_offset
#
#   - Folder/ : the name of the folder containing ONLY the Substrated files form SEC-SAXS.
#   - `qmin_offset` : the offset (in number of lines) to be added to the first usable line to determine qmin, use the value from PRIMUS or RAW.
#   - `qmax_offset`: the offset (in number of lines) to be added to the first usable line to determine qmax use the value from PRIMUS or RAW.
#
## Features
# 1. Guinier approximation :
# - Read each .dat files and determine first usable line base on the provided qmin_offset qmax_offset.
# - Extraction of data for q and I(q) in the selected range.
# - Perform a linear regression to calculate Rg (radius of gyration) and I0 (intensity at q=0).
# - Write data to text file.
# - Display graph with I(0) and Rg vs Frame index
#
# 2. Volume of corelation (VC):
# - Extract data up to q=0.3.
# - Calculate the integral of the product I(q)*q.
# - Calculation of VC, QR (quality factor) and MW (molecular weight).
# - Write data to text file.
# - Display graph with I(0) and MW vs Frame index
# 
## Tests
# Works on mac M1 and Linux. It has been tested only on SEC-SAXS data from SWING beamline at Soleil-synchrotron France.
#(but should work on different beamlines)
# Jean-Marie Bourhis and Chat-GPT via mac-gpt (because I'm a "tanche" in python programming)
# 2023
###################################################################

import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
import os
import sys


def calculate_diffusion(Rg, I0, q):
    I = I0 * np.exp(-q**2 * Rg**2 / 3)  
    return q, I

# Check if the command line arguments are provided correctly
if len(sys.argv) < 4:
    print("Please provide the necessary arguments: script_name.py data_folder_path qmin_offset qmax_offset")
    sys.exit(1)

# Path to the folder containing the .dat files
folder_path = str(sys.argv[1])
qmin_offset = int(sys.argv[2])
qmax_offset = int(sys.argv[3])

# List to store the results
resultats = []

# Iterate through all .dat files in the folder
file_names = sorted(os.listdir(folder_path))  # Sorting file names in alphabetical order
for index, file_name in enumerate(file_names):
    if file_name.endswith(".dat"):
        # Load data from the file
        with open(os.path.join(folder_path, file_name), 'r') as file:
            lines = file.readlines()

       # Find the first usable line
        first_usable_line = None
        for i, line in enumerate(lines):
            line = line.strip()
            if line and len(line.split()) >= 3:
                try:
                    values = [float(x) for x in line.split()[:3]]
                    if not any(np.isnan(values)):
                        first_usable_line = i
                        break
                except ValueError:
                    continue

        if first_usable_line is None:
            print("No usable line found in the file.")
            continue

       # Extract data columns
        data = np.loadtxt(lines[first_usable_line:], comments='#')

        # Extract q and I(q) data columns

        q = data[:, 0]
        I = data[:, 1]

#####################################
#
# GUINIER
#
#####################################

        # Find qmin et qmax
        qmin_ligne = first_usable_line + qmin_offset + 1
        qmax_ligne = first_usable_line + qmax_offset + 1

        # Extract qmin et qmax
        qmin = q[qmin_ligne]
        qmax = q[qmax_ligne]
        I_qmin = I[qmin_ligne]
        I_qmax = I[qmax_ligne]

        print("File :", file_name)
        print("first line :", first_usable_line)
        print("qmin :", qmin, "(ligne", qmin_ligne, "), I(qmin) =", I_qmin)
        print("qmax :", qmax, "(ligne", qmax_ligne, "), I(qmax) =", I_qmax)

        # Range for the linear regression
        q_range = q[(q >= qmin) & (q <= qmax)]
        I_range = I[(q >= qmin) & (q <= qmax)]

        # calculate Rg and I(0)
        m, c = np.polyfit(q_range**2, np.log(I_range), deg=1)
        Rg = np.sqrt(-3 * m)
        I0 = np.exp(c)
        # Calculate qmin * Rg et qmax * Rg
        qmin_Rg = qmin * Rg
        qmax_Rg = qmax * Rg

#####################################
#
# Volume of correlation 
#
#####################################

       # Filter data up to q=0.3
        q_filtered = q[q <= 0.3]
        I_filtered = I[q <= 0.3]

       # define the Y axis with yvc
        yvc = I_filtered * q_filtered

       # define the integrale Intgr
        Intgr = integrate.simps(yvc, q_filtered)

       # Calculate VC, QR and MW
        VC = I0 / Intgr
        QR = VC**2 / Rg
        MW1 = QR / 0.1231

#####################################
#
# OUTPUT 
#
#####################################      
       
        # print the reults
        print("Rg:", Rg)
        print("I0:", I0)
        print("qmin * Rg:", qmin_Rg)
        print("qmax * Rg:", qmax_Rg)
        print("MW cut q=0.3:", MW1)
        # add results to a list
        resultats.append((file_name, index, I0, Rg, MW1))

        # Write ouput Index, I(0), Rg 
with open("Ragtime_01.txt", "w") as f:
    f.write("Index\tI(0)\tRg\n")
    for result in resultats:
        f.write("{}\t{}\t{}\n".format(result[1], result[2], result[3]))
        # Write ouput Index, I(0), MW 
with open("MW_02.txt", "w") as f:
    f.write("Index\tI(0)\tMW1\n")
    for result in resultats:
        f.write("{}\t{}\t{}\n".format(result[1], result[2], result[4]))

#####################################
#
# PLOTS 
#
#####################################

## I(o), Rg vs Frames

# Read data from Ragtime_01.txt
data = np.loadtxt("Ragtime_01.txt", delimiter='\t', skiprows=1, usecols=(0, 1, 2))

# Eextract datas
index = data[:, 0]
I0 = data[:, 1]
Rg = data[:, 2]

# setup the plot 
fig, ax1 = plt.subplots()

# Plot I(0) on the Y right axis
color = 'tab:red'
ax1.set_xlabel('Frame Index')
ax1.set_ylabel('I(0)', color=color)
ax1.plot(index, I0, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Make a second Y axis for Rg 
ax2 = ax1.twinx()

# Plot Rg on the left Y axis
color = 'tab:blue'
ax2.set_ylabel('Rg', color=color)
ax2.plot(index, Rg, color=color)
ax2.tick_params(axis='y', labelcolor=color)

# Add a legend
ax1.legend(['I(0)'], loc='upper left')
ax2.legend(['Rg'], loc='upper right')

# display graph 
plt.title('SEC-SAXS, I(0) and Rg vs Frames')
plt.show()

## I(o), MW vs Frames

# Read data from MW_02.txt
data = np.loadtxt("MW_02.txt", delimiter='\t', skiprows=1, usecols=(0, 1, 2))

# Extract datas
index = data[:, 0]
I0 = data[:, 1]
MW = data[:, 2]

# # setup the plot 
fig, ax1 = plt.subplots()

# Plot I(0) on the Y right axis
color = 'tab:red'
ax1.set_xlabel('Frame Index')
ax1.set_ylabel('I(0)', color=color)
ax1.plot(index, I0, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Make a second Y axis for MW 
ax2 = ax1.twinx()

# Plot MW on the left Y axis
color = 'tab:blue'
ax2.set_ylabel('MW', color=color)
ax2.plot(index, MW, color=color)
ax2.tick_params(axis='y', labelcolor=color)

# Add a legend
ax1.legend(['I(0)'], loc='upper left')
ax2.legend(['MW'], loc='upper right')

# Display the plot 
plt.title('SEC-SAXS I(0) and MW vs Frames')
plt.show()
