###################################################################
# This script allows you to analyze and plot the elution profile of
# your SEC-SAXS experiment using data from Subtracted files in the  folder FOLDER/.
# It creates two text files: 
# 1- Ragtime_01.txt containing Index of the frame, I(0) and Rg values,
# 2- MW_02.txt containing Index of the frame, I(0) and MW1 values.
# You can use software like Excel, Prism, SigmaPlot, etc., to plot the data as you want. You can also keep the graphs display by the script as a picture.
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
# 2. Volume of correlation (VC):
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

# Read data from Ragtime_01.txt for the first plot, with nan filtering
data_rg = np.loadtxt("Ragtime_01.txt", delimiter='\t', skiprows=1, usecols=(0, 1, 2))

# Extract index, I(0), and Rg
index_rg = data_rg[:, 0]
I0_rg = data_rg[:, 1]
Rg = data_rg[:, 2]

# Filter out NaN values from I(0) and corresponding Rg and index
valid_indices = ~np.isnan(I0_rg)  # Boolean array of valid (non-NaN) entries
index_rg = index_rg[valid_indices]
I0_rg = I0_rg[valid_indices]
Rg = Rg[valid_indices]

# Find the maximum I(0) and the corresponding Rg and frame
max_I0_rg = np.max(I0_rg)
max_Rg = Rg[np.argmax(I0_rg)]
frame_number = index_rg[np.argmax(I0_rg)]  # Frame number for the max I(0)

# Read data from MW_02.txt for the second plot
data_mw = np.loadtxt("MW_02.txt", delimiter='\t', skiprows=1, usecols=(0, 1, 2))

# Extract index, I(0), and MW
index_mw = data_mw[:, 0]
I0_mw = data_mw[:, 1]
MW = data_mw[:, 2]

# Filter out NaN values from I(0) and MW for the second plot
valid_indices_mw = ~np.isnan(I0_mw)
index_mw = index_mw[valid_indices_mw]
I0_mw = I0_mw[valid_indices_mw]
MW = MW[valid_indices_mw]

# Find the maximum I(0) and corresponding MW for the second plot
max_I0_mw = np.max(I0_mw)
max_MW = MW[np.argmax(I0_mw)]

# Create a figure with two subplots (top-bottom) that share the same x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 10))

#####################################
# First plot: I(0) and Rg vs Frames
#####################################
color = 'tab:red'
ax1.set_ylabel('I(0)', color=color)
ax1.plot(index_rg, I0_rg, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Add a second Y-axis for Rg
ax1_twin = ax1.twinx()
color = 'tab:blue'
ax1_twin.set_ylabel('Rg', color=color)
ax1_twin.plot(index_rg, Rg, color=color)
ax1_twin.tick_params(axis='y', labelcolor=color)


# Title for the first subplot
ax1.set_title('SEC-SAXS I(0) and Rg vs Frames')

# Add a small box with I(0) max, frame number, Rg, qmin_offset, qmax_offset
annotation_text = (f"I(0) max: {max_I0_rg:.2f}\n"
                   f"Frame: {int(frame_number)}\n"
                   f"Rg: {max_Rg:.2f}\n"
                   f"qmin_offset: {qmin_offset}\n"
                   f"qmax_offset: {qmax_offset}")
# Add a legend with the maximum I(0) and corresponding MW
ax1.legend([f"I(0)"], loc='upper left')
ax1_twin.legend([f"Rg"], loc='upper right')

ax1.annotate(annotation_text,
             xy=(0.2, 0.05),  # Coordinates (x=5%, y=5%) relative to the axis
             xycoords='axes fraction',  # Position relative to the plot area (fraction of the axis)
             bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="wheat",alpha=0.5),
             ha='left')  # Left-align the box

#####################################
# Second plot: I(0) and MW vs Frames
#####################################
color = 'tab:red'
ax2.set_xlabel('Frame Index')
ax2.set_ylabel('I(0)', color=color)
ax2.plot(index_mw, I0_mw, color=color)
ax2.tick_params(axis='y', labelcolor=color)

# Add a second Y-axis for MW
ax2_twin = ax2.twinx()
color = 'tab:blue'
ax2_twin.set_ylabel('MW', color=color)
ax2_twin.plot(index_mw, MW, color=color)
ax2_twin.tick_params(axis='y', labelcolor=color)

# Add a legend with the maximum I(0) and corresponding MW
ax2.legend([f"I(0)"], loc='upper left')
ax2_twin.legend([f"MW"], loc='upper right')

# Title for the second subplot
ax2.set_title('SEC-SAXS I(0) and MW vs Frames')


# Add a small box with I(0) max, frame number, Rg, qmin_offset, qmax_offset
annotation_text = (f"I(0) max: {max_I0_rg:.2f}\n"
                   f"Frame: {int(frame_number)}\n"
                   f"MW: {max_MW:.2f}\n"
                   f"qmin_offset: {qmin_offset}\n"
                   f"qmax_offset: {qmax_offset}")

ax2.annotate(annotation_text,
             xy=(0.2, 0.05),  # Coordinates (x=5%, y=5%) relative to the axis
             xycoords='axes fraction',  # Position relative to the plot area (fraction of the axis)
             bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="wheat",alpha=0.5),
             ha='left')  # Left-align the box
ax1.grid(True)
ax2.grid(True)
# Adjust layout for better spacing
plt.tight_layout()

# Save and display the final plot
plt.savefig('SEC-SAXS_combined_I0_Rg_MW_vs_Frames_with_annotation.png')
plt.savefig('SEC-SAXS_combined_I0_Rg_MW_vs_Frames_with_annotation.svg',format="svg") 
plt.show()