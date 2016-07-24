from BeautifulSoup import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import threading
import selenium
import mechanize
import re
import time
import csv
import os

# Main variables
LoginPage = 'https://www.dataflowbpm.com/sbm/bpmportal/login.jsp'
CaseSrcPg = 'https://www.dataflowbpm.com/sbm/bpmportal/ExternalUtils/LiveSearch/Case_Search.jsp'
CasePg = 'https://www.dataflowbpm.com/sbm/BizSolo/common/jsp/DuplicateCaseData_test.jsp?LEGACY=NO&subBarcode1=NA&subPid=0&BarCode='
FramePg = 'https://www.dataflowbpm.com/sbm/BizSolo/common/jsp/DuplicateTaskData.jsp?Barcode='
LoginID = 'hassanjs'
LoginPass = 'Hassan@11'
Curfolder = os.getcwd()
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36")
tlock = threading.Lock()

# Login Savvion site

class CompFetcher(threading.Thread):
    def __init__(self, seldriver,  barcode, newlink, inpfile):
        threading.Thread.__init__(self)
        self.barcode = barcode
        self.newlink = newlink
        self.inpfile = inpfile
        self.selmndrv = seldriver

        # print threading.current_thread().getName() + ' Started!'
        print self.barcode + ' - Thread started!'
        self.selmndrv.get(self.newlink)
        self.soup = BeautifulSoup(self.selmndrv.page_source)
        if not os.path.exists(Curfolder + '/Barcodes/'):
            os.makedirs(Curfolder + '/Barcodes/')
        barcodefile = open(Curfolder + '/Barcodes/' + str(self.barcode) + '.html', 'wb')
        barcodefile.write(str(self.soup))
        barcodefile.close()
        outputflag = open(str(self.inpfile) + '_records.csv', 'ab')
        outputflag.write(barcode)
        outputflag.write('\n')
        outputflag.close()
        # print 'Fetching # ' + str(self.barcode)
        for allduplicates in self.soup.findAll('a', attrs={'onclick': re.compile('showFrameData.*')}):
            substring = re.findall('showFrameData\(.(.+).\)', str(allduplicates))
            firstval = re.split('.,.', str(substring))
            code1 = re.findall('(\d+)', firstval[0])
            code2 = re.findall('(\d+)', firstval[6])
            subbarcode = firstval[1]
            component = firstval[2]
            framelink = FramePg + str(self.barcode) + '&SubBarcode=' + str(subbarcode) + '&PID=' + \
                        str(code1[0]) + '&Component=' + str(component) + '&CheckID=1&WORKSTEPNAME=DVS&subPID=' \
                        + str(code2[0])
            # print threading.current_thread().getName() + ' => ' + str(framelink)
            self.selmndrv.get(framelink)
            subsoup = BeautifulSoup(self.selmndrv.page_source)
            try:
                eRRmsgflag = subsoup.findAll('span', attrs={'class':'Error'})
                if not eRRmsgflag[0] == None:
                    tlock.acquire()
                    SavLogin()
                    tlock.release()
            except:
                if not os.path.exists(Curfolder + '/Components/'):
                    os.makedirs(Curfolder + '/Components/')
                if not os.path.exists(Curfolder + '/Components/' + str(component)):
                    os.makedirs(Curfolder + '/Components/' + str(component))
                sbbarcodefile = open(Curfolder + '/Components/' + str(component) + '/' + str(subbarcode) + '.html', 'wb')
                sbbarcodefile.write(str(subsoup))
                sbbarcodefile.close()
                compOutput = open(str(Inputfile) + '_components.csv', 'ab')
                compOutput.write(framelink)
                compOutput.write('\n')
                compOutput.close()

def SavLogin():
    global seldriver
    seldriver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true'])
    seldriver.get(LoginPage)
    seldriver.set_window_size(1024, 768)
    seldriver.save_screenshot('snapshot # Login.png')
    seldriver.find_element_by_name('BizPassUserID').send_keys(LoginID)
    seldriver.find_element_by_name('BizPassUserPassword').send_keys(LoginPass)
    seldriver.find_element_by_name('login').submit()
    seldriver.implicitly_wait(1)
    seldriver.save_screenshot('snapshot # Login.png')

def MainFunc():
    global Inputfile
    Inputfile = raw_input('Name of CSV Input File : ')
    print "Loading site, be patient..."
    if os.path.exists(Inputfile):
        csvfile = open(Inputfile, 'rb')
        try:
            rownum = 0
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                rownum = rownum + 1
                if rownum > 1:
                    barcode = row[1]
                    # print "Barcode = %s queued" %barcode
                    thecode = re.findall('\'(\d{4,})\'', row[0])
                    newlink = CasePg + str(barcode) + '&PID=' + str(thecode[0])
                    backgrnd = CompFetcher(seldriver, barcode, newlink, Inputfile)
                    backgrnd.start()
                    time.sleep(2)
        except Exception as ex:
            print "Error code %s" % ex
        finally:
            csvfile.close()
    else:
        print 'File not found!'
    seldriver.close()
    print "All done!"
    exit()

if __name__ == '__main__':
    print "Initializing Savvion Scrapper"
    SavLogin()
    MainFunc()
