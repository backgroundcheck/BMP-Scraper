# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".


from BeautifulSoup import BeautifulSoup
from selenium import webdriver
import selenium
import mechanize
import scraperwiki
import lxml.html
import re
import csv
import os
# Main variables
LoginPage = 'https://www.dataflowbpm.com/sbm/bpmportal/login.jsp'
CaseSrcPg = 'https://www.dataflowbpm.com/sbm/bpmportal/ExternalUtils/LiveSearch/Case_Search.jsp'
CasePg = 'https://www.dataflowbpm.com/sbm/BizSolo/common/jsp/DuplicateCaseData_test.jsp?LEGACY=NO&subBarcode1=NA&subPid=0&BarCode='
FramePg = 'https://www.dataflowbpm.com/sbm/BizSolo/common/jsp/DuplicateTaskData.jsp?Barcode='
LoginID = 'hassanjs'
LoginPass = 'Hassan@33'
Curfolder = os.getcwd()


# Inputfile = 'Savvion Codes.csv'


# Login Savvion site
seldriver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
# seldriver = webdriver.Firefox()
seldriver.get(LoginPage)
seldriver.set_window_size(1024, 768)
seldriver.save_screenshot('snapshot # Login.png')
seldriver.find_element_by_name('BizPassUserID').send_keys(LoginID)
seldriver.find_element_by_name('BizPassUserPassword').send_keys(LoginPass)
seldriver.find_element_by_name('login').submit()
seldriver.implicitly_wait(1)
seldriver.save_screenshot('snapshot # Login.png')

Inputfile = raw_input('Name of CSV Input File : ')
if os.path.exists(Inputfile):
    csvfile = open(Inputfile, 'rb')
    try:
        rownum = 0;
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rownum = rownum + 1
            if rownum > 1:
                barcode = row[1]
                thecode = re.findall('\'(\d{4,})\'', row[0])
                newlink = CasePg + str(barcode) + '&PID=' + str(thecode[0])
                seldriver.get(newlink)
                # seldriver.save_screenshot('snapshot # ' + str(barcode) + '.png')
                soup = BeautifulSoup(seldriver.page_source)
                if not os.path.exists(Curfolder + '/Barcodes/'):
                    os.makedirs(Curfolder + '/Barcodes/')
                barcodefile = open(Curfolder + '/Barcodes/' + str(barcode) + '.html', 'wb')
                barcodefile.write(str(soup))
                barcodefile.close()
                outputflag = open(str(Inputfile) + '_records.csv', 'ab')
                outputflag.write(barcode)
                outputflag.write('\n')
                outputflag.close()
                print 'Fetching # ' + str(barcode)
                # counter = 0
                for allduplicates in soup.findAll('a', attrs={'onclick': re.compile('showFrameData.*')}):
                    # print allduplicates
                    substring = re.findall('showFrameData\(.(.+).\)', str(allduplicates))
                    firstval = re.split('.,.', str(substring))
                    code1 = re.findall('(\d+)', firstval[0])
                    code2 = re.findall('(\d+)', firstval[6])
                    subbarcode = firstval[1]
                    component = firstval[2]
                    framelink = FramePg + str(barcode) + '&SubBarcode=' + str(subbarcode) + '&PID=' +\
                                str(code1[0]) + '&Component=' + str(component) + '&CheckID=1&WORKSTEPNAME=DVS&subPID='\
                                + str(code2[0])
                    seldriver.get(framelink)
                    subsoup = BeautifulSoup(seldriver.page_source)
                    if not os.path.exists(Curfolder + '/Components/'):
                        os.makedirs(Curfolder + '/Components/')
                    if not os.path.exists(Curfolder + '/Components/' + str(component)):
                        os.makedirs(Curfolder + '/Components/' + str(component))
                    sbbarcodefile = open(Curfolder + '/Components/' + str(component) + '/'+ str(subbarcode) + '.html', 'wb')
                    sbbarcodefile.write(str(subsoup))
                    sbbarcodefile.close()
                    compOutput = open(str(Inputfile) + '_components.csv', 'ab')
                    compOutput.write(framelink)
                    compOutput.write('\n')
                    compOutput.close()
    finally:
        csvfile.close()
else:
    print 'File not found!'

seldriver.close()

