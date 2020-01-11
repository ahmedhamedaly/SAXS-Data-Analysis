import math
import statistics
import os
import tkinter as tk
import matplotlib.pyplot as plt
import pytemperature
from tkinter import filedialog
from fpdf import FPDF
from PyPDF2 import PdfFileMerger


# peaks = peak(angle, intensity, resolution, normIntensity)
# @Parameters: angle, intensity, resolution, normalised intensity
# @Returns: peakList
# Finds the peaks and adds them to a list


def peak(a, i, r, ni):
    peakList = []
    peakCoords = []
    for index in range(len(i)):
        # finds a peak in the y axis
        try:
            if i[index] > i[index - 1] > i[index - 2] > i[index - 3] > i[index - 4] and i[index] > i[index + 1] > i[index + 2] > i[index + 3] > i[index + 4]:
                # Adds the peaks to a list
                peakList.append((a[index], r[index]))
                peakCoords.append((round(a[index], 2), round(ni[index], 2)))
        except IndexError:
            print("Peak fucked up...")

    return peakList, peakCoords


# ratios = ratio(peaks)
# @Parameters: peaks
# @Return: ratioList
# Assigns the first peak as 1 as find the ratio of the rest


def ratio(p, cp):
    ratioList1 = []
    coordPeakList1 = []

    # First Ratio
    r1 = 0
    for index in range(len(p)):
        # First iteration
        if index == 0:
            r1 = p[index][0]
            # Assigns the first ratio to 1
            ratioList1.append((1, p[index][1]))
            coordPeakList1.append(cp[index])
        else:
            # Rounds the ratio to 2 decimal points
            r = round(p[index][0] / r1, 2)
            ratioList1.append((r, p[index][1]))
            coordPeakList1.append(cp[index])

    ratioList2 = []
    coordPeakList2 = []
    r2 = 0
    for index in range(len(p)):
        if index == 0:
            pass
        elif index == 1:
            r2 = p[index][0]
            ratioList2.append((1, p[index][1]))
            coordPeakList2.append(cp[index])
        else:
            r = round(p[index][0] / r2, 2)
            ratioList2.append((r, p[index][1]))
            coordPeakList2.append(cp[index])

    ratioList3 = []
    coordPeakList3 = []
    r3 = 0
    for index in range(len(p)):
        if index == 0 or index == 1:
            pass
        elif index == 2:
            r3 = p[index][0]
            ratioList3.append((1, p[index][1]))
            coordPeakList3.append(cp[index])
        else:
            r = round(p[index][0] / r3, 2)
            ratioList3.append((r, p[index][1]))
            coordPeakList3.append(cp[index])

    return ratioList1, ratioList2, ratioList3, coordPeakList1, coordPeakList2, coordPeakList3


# phases = phase(ratios, coordpeaks)
# @Parameters: ratios, coordpeaks
# @Returns: phaseList
# Takes the ratio and maps it to a phase and also the peaks of each phase


def phase(r, cp):
    phaseList = {
        "l": [],
        "h": [],
        "ia3d": [],
        "pn3m": [],
        "fi": []
    }

    coordsList = {
        "l": [],
        "h": [],
        "ia3d": [],
        "pn3m": [],
        "fi": []
    }

    # Characteristic Value in Ratios
    for index, cv in enumerate(r):
        for key, values in phasesDict.items():
            # Checks the phase
            if key == 'l':
                for value in values:
                    # Continue if its close by +- 0.025
                    if abs(cv[0] - value) <= 0.025:
                        # Creates a tuple of the resolution and hkl
                        tmp = (cv[1], phaseMiller[key][value])
                        phaseList[key].append(tmp)
                        coordsList[key].append(cp[index])

            if key == 'h':
                for value in values:
                    # Continue if its close by +- 0.025
                    if abs(cv[0] - value) <= 0.025:
                        # Creates a tuple of the resolution and hkl
                        tmp = (cv[1], phaseMiller[key][value])
                        phaseList[key].append(tmp)
                        coordsList[key].append(cp[index])

            if key == 'ia3d':
                for value in values:
                    if abs(cv[0] - value) <= 0.025:
                        tmp = (cv[1], phaseMiller[key][value])
                        phaseList[key].append(tmp)
                        coordsList[key].append(cp[index])

            if key == 'pn3m':
                for value in values:
                    if abs(cv[0] - value) <= 0.025:
                        tmp = (cv[1], phaseMiller[key][value])
                        phaseList[key].append(tmp)
                        coordsList[key].append(cp[index])

            if key == 'fi':
                for value in values:
                    if abs(cv[0] - value) <= 0.025:
                        tmp = (cv[1], phaseMiller[key][value])
                        phaseList[key].append(tmp)
                        coordsList[key].append(cp[index])

    return phaseList, coordsList


# lps = latticeParameter(phases)
# @Parameters: phases
# @Returns: Phases identified
# Determines if the element is found or not


def latticeParameter(p):
    lp = {
        "l": [],
        "h": [],
        "ia3d": [],
        "pn3m": [],
        "fi": []
    }

    # If n of the m ratios are available then phase present
    if len(p['pn3m']) >= 3:
        lp['pn3m'] = [tu[0] * tu[1] for tu in p['pn3m']]
    if len(p['ia3d']) >= 3:
        lp['ia3d'] = [tu[0] * tu[1] for tu in p['ia3d']]
    if len(p['l']) == 2:
        lp['l'] = [tu[0] * tu[1] for tu in p['l']]
    if len(p['h']) == 3:
        lp['h'] = [tu[0] * tu[1] for tu in p['h']]
    if len(p['fi']) == 1:
        lp['fi'] = [tu[0] * tu[1] for tu in p['fi']]
        # for tu in p['fi']:
        #     lp['fi'].append(tu[0] * tu[1])

    return lp


# Stats = meansAndStd(Lattice parameter, ratios, coords)
# @Parameters: Lattice parameter, Ratios, Coords
# @Returns: Average and Standard Deviation and peak coords
# Gets the mean and average of the data and the peak coords


def meanAndStd(lp, r, c):
    text = []
    for key, value in lp.items():
        if printed[key] == 0 and len(value) >= 3 and key != 'h':
            printed[key] = 1
            a = round(statistics.mean(value), 2)
            s = round(statistics.stdev(value), 2)
            text.append(f"Ratio: {r}")
            text.append(f"Phase: {key}")
            text.append(f"Average: {a}")
            text.append(f"Standard Deviation: {s}")
            text.append(f"Peak Coordinates: ")
            coordsList = [str(coord) for coord in c[key]]

            write(text, 'L')
            pdf.set_font('Times', "", 12.0)

            for coord, lps in zip(coordsList, value):
                pdf.cell(ln=3, h=6.5, align=a, w=0, txt=coord + " : " + str(round(lps, 2)), border=100)

            pdf.set_font('Times', "", 16)
            write(newLine, 'L')

            return

    for key, value in lp.items():
        if printed[key] == 0 and len(value) == 3 and key == 'h':
            printed[key] = 1
            a = round(statistics.mean(value), 2)
            s = round(statistics.stdev(value), 2)
            text.append(f"Ratio: {r}")
            text.append(f"Phase: {key}")
            text.append(f"Average: {a}")
            text.append(f"Standard Deviation: {s}")
            text.append(f"Peak Coordinates: ")
            coordsList = [str(coord) for coord in c[key]]

            write(text, 'L')
            pdf.set_font('Times', "", 12.0)

            for coord, lps in zip(coordsList, value):
                pdf.cell(ln=3, h=6.5, align=a, w=0, txt=coord + " : " + str(lps), border=100)

            pdf.set_font('Times', "", 16)
            write(newLine, 'L')

            return
        elif printed[key] == 0 and len(value) == 2 and key == 'l':
            printed[key] = 1
            a = round(statistics.mean(value), 2)
            s = round(statistics.stdev(value), 2)
            text.append(f"Ratio: {r}")
            text.append(f"Phase: {key}")
            text.append(f"Average: {a}")
            text.append(f"Standard Deviation: {s}")
            text.append(f"Peak Coordinates: ")
            coordsList = [str(coord) for coord in c[key]]

            write(text, 'L')
            pdf.set_font('Times', "", 12.0)

            for coord, lps in zip(coordsList, value):
                pdf.cell(ln=3, h=6.5, align=a, w=0, txt=coord + " : " + str(lps), border=100)

            pdf.set_font('Times', "", 16)
            write(newLine, 'L')

            return


# write(text, alignment)
# @Parameters: text, alignment
# @Returns: None
# Writes the text to the pdf


def write(t, a):
    for x in t:
        pdf.cell(ln=3, h=6.5, align=a, w=0, txt=x, border=100)


phasesDict = {
    "l": [1.00, 2.00],
    "h": [1.00, 2.00, 2.45],
    "ia3d": [1.00, 1.15, 1.53, 1.63, 1.83, 1.91],
    "pn3m": [1.00, 1.22, 1.41, 1.73, 2.00, 2.12],
    "fi": [1.00]
}

phaseMiller = {
    "l": {
        1.00: 1,
        2.00: 2
    },
    "h": {
        1.00: 1,
        2.00: 1.732050808,
        2.45: 2
    },
    "ia3d": {
        1.00: 2.44949,
        1.15: 2.828427,
        1.53: 3.741657,
        1.63: 4,
        1.83: 4.472136,
        1.91: 4.690416
    },
    "pn3m": {
        1.00: 1.414214,
        1.22: 1.732051,
        1.41: 2,
        1.73: 2.44949,
        2.00: 2.828427,
        2.12: 3
    },
    "fi": {
        1.00: 1
    }
}

newLine = [
    "\n",
    "\n"
]

saveFile = ""
merger = PdfFileMerger()
root = tk.Tk()
root.withdraw()
# file = filedialog.askopenfile(parent=root, mode='r', title='Choose a file', filetypes=[('Data File', '*.xye')])

# Opening up the files
files = filedialog.askopenfilenames(parent=root, title='Choose a file', filetypes=[('Data File', '*.xye')])

# Splitting the files
file = root.tk.splitlist(files)

# How far the cut off of the x Axis is
cut = 2.5

# Setting the cut off if the file starts with -
try:
    # Gets the first file name
    firstFile = os.path.splitext(os.path.basename(files[0]))[0]

    # Checks if the first file starts with a - so it can set the cut off
    if firstFile.startswith('-'):
        # Replaces the - with empty space and extracts the int
        firstFile.replace('-', '')
        cut = abs(int(firstFile))
        files = files[1:]
except IndexError:
    exit(1)


for f in files:

    # Opens the file
    file = open(f, 'r')

    # Dict of printed phases
    printed = {
        "l": 0,
        "h": 0,
        "ia3d": 0,
        "pn3m": 0,
        "fi": 0
    }

    if file is None:
        # tk.messagebox.showinfo("Empty File", "You added an empty file with nothing inside.")
        exit(1)

    # The file name
    nameFile = os.path.splitext(os.path.basename(file.name))[0]

    # The directory the file will be saved to
    dirFile = os.path.dirname(file.name)

    # Determines the name of the save file
    if len(files) > 1:
        saveFile = dirFile + '/' + 'Result.pdf'
    else:
        saveFile = dirFile + '/' + nameFile + '_Result.pdf'

    # Title of the file
    title = [
        nameFile
    ]

    # The data  from the file
    data = file.readlines()

    # Necessary information for the data
    angle = []
    intensity = []
    resolution = []

    for line in data:
        line = (" ".join((line.split()))).split()
        # Keep X axis to 3 by default of as said
        if float(line[0]) > cut:
            break
        # X axis: line[0] = angle (2Θ)
        angle.append(float(line[0]))
        # Y axis: line[1] = intensity
        intensity.append(float(line[1]))
        # resolution = 0.984081/(2*(Sin(2Θ)))
        resolution.append(0.984081 / (2 * (math.sin(math.radians(float(line[0])/2)))))

    # Figure of plot
    fig = plt.figure()

    # Normalising the y axis to max of 1
    normIntensity = [(inte - min(intensity)) / (max(intensity) - min(intensity)) for inte in intensity]

    # Plotting with thin line width
    plt.plot(angle, normIntensity, linewidth=0.75)
    # plt.plot(angle, intensity, linewidth=0.75)

    # Getting title
    sn = nameFile.split('_')

    plotTitle = "Angle (2Θ) vs Intensity"
    try:
        k = float(sn[5].replace('T', '').replace('K', ''))
        kToC = pytemperature.k2c(k)
        plotTitle = sn[0] + "  " + sn[1] + "  " + sn[3] + "  " + sn[5] + "  " + '[' + str(round(kToC)) + 'degC' + ']'
    except ValueError:
        try:
            k = float(sn[3].replace('T', '').replace('K', ''))
            kToC = pytemperature.k2c(k)
            plotTitle = sn[0] + "  " + sn[1] + "  " + sn[2] + "  " + '[' + str(round(kToC)) + 'degC' + ']'
        except ValueError:
            pass

    plt.title(plotTitle)

    # Labeling axis
    plt.xlabel("Angle (2Θ)")
    plt.ylabel("Intensity")

    # Show grid
    plt.grid(True)

    # Showing Plot
    # plt.show()

    # Determine the peaks given the angle, intensity and resolution and coords of them
    peaks, coordPeaks = peak(angle, intensity, resolution, normIntensity)

    # Determine the 3 ratios given the peaks
    ratios1, ratios2, ratios3, coordPeak1, coordPeak2, coordPeak3 = ratio(peaks, coordPeaks)

    # Starts a pdf file and adds a page
    pdf = FPDF()
    pdf.add_page()

    # The title of the pdf
    pdf.set_font("Times", "BU", 12)
    write(title, 'C')

    # Adds a line spacing
    pdf.set_font('Times', "", 16)
    write(newLine, 'L')

    # --------------------------------------------

    phases1, coords = phase(ratios1, coordPeak1)
    latticeParameters1 = latticeParameter(phases1)
    meanAndStd(latticeParameters1, 1, coords)

    phases2, coords = phase(ratios2, coordPeak2)
    latticeParameters2 = latticeParameter(phases2)
    meanAndStd(latticeParameters2, 2, coords)

    phases3, coords = phase(ratios3, coordPeak3)
    latticeParameters3 = latticeParameter(phases3)
    meanAndStd(latticeParameters3, 3, coords)

    # --------------------------------------------

    # Save the figure
    fig.savefig('page1.pdf')

    # Saves the result pdf
    pdf.output('page2.pdf', 'F')

    # List of pdfs for merging
    pdfs = ['page1.pdf', 'page2.pdf']

    pdf.close()

    # Adds the 2 pdfs together
    for pdf in pdfs:
        merger.append(pdf)

    # Deletes the pdfs
    for pdf in pdfs:
        os.remove(pdf)


# Saves the merged file with the set save file name
merger.write(saveFile)

merger.close()

print("done")
