# genLabReport.py - generate PDF report with embedded QR code with test results
# provided in a CSV input file containing data for one or more samples

import sys
import csv
import qrcode
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
import os

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def generateQRCode(rptD):
    qrc = qrcode.QRCode(version=10,error_correction=qrcode.constants.ERROR_CORRECT_H)
    data = "SRF ID : {} \n ICMR ID: {} \n IISc ID: {} \n Name: {} \n Age: {} \n Gender: {} \n Swab Collected On: {} \n Lab Name: Indian Institute of Science, Bangalore\n Result Date: {} \n Test Type: RT-PCR\n Test Result: {}.\n".format(rptD['srfid'],rptD['sampleICMRID'],rptD['sampleIIScID'],rptD['patientName'],rptD['patientAge'],rptD['patientGender'],rptD['sampleCollectionDate'],rptD['testDate'],rptD['testResult'])
    qrc.add_data(data)
    qrImg = qrc.make_image(fill_color="black", back_color="white")
    qrImg.save(rptD['qrcodeImgFile'])
    return

def prepareData( row ):
    rptData = {}

    rptData['reportDate'] = row[' Date of Sample Tested']
    rptData['sampleCollectionDate'] = row[' Date of Sample Collection']
    rptData['sampleRcptDateTime'] = row[' Date of Sample Received']
    rptData['sampleIIScID'] = row[' Sample ID']
    rptData['sampleICMRID'] = row['Icmr ID']
    rptData['srfid'] = row[' SRF ID']
    rptData['patientName'] = row[' Patient Name']
    rptData['patientAge'] = row[' Age']
    rptData['patientGender'] = row[' Gender']
    rptData['sampleType'] = row[' Sample Type']
    rptData['testDate'] = row[' Date of Sample Tested']
    rptData['testResult'] = row[' Final Result Sample']
    rptData['qrcodeImgFile'] = 'qr_' + row[' SRF ID'] + '.png'
    generateQRCode(rptData)
    return rptData

def generatePDFReport( row ):
    outFilename = row[' SRF ID'] + '.pdf'
    # fill template with sample result values
    # generate report
    # generate qr code
    # convert to pdf
    print("Creating report %s ..." % outFilename)
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR + '/templates'),
                         trim_blocks=True)
    rd = prepareData( row )
    rptHtml = j2_env.get_template('report_template.html').render(reportData = rd)
    reportFile = open('reports/' + rd['srfid'] + '.pdf','w+b')
    pisa_status = pisa.CreatePDF(rptHtml, dest = reportFile)
    if not pisa_status.err:
        print("Created PDF report %s."%outFilename)
    os.remove(rd['qrcodeImgFile'])
    return

if (len(sys.argv) < 1):
    print("Usage: genLabReport.py <results_file.csv>")
    sys.exit(1)

#with open("samp_results.csv") as resultsCSVFile:
with open(sys.argv[1]) as resultsCSVFile:
    reader = csv.DictReader(resultsCSVFile)
    for row in reader:
        generatePDFReport(row)
