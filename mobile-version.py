from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import datetime
import sys, getopt
import random
import re
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.common.by as By

def LoadUserAgents(uafile="user_agents.txt"):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas


def diff_days(a,b):
    '''
    Returns the diference of days
    :param a: like "2017-12-30"
    :param b: same
    :return: difference of days as int
    '''
    a = datetime.datetime.strptime(a, "%Y-%m-%d")
    b = datetime.datetime.strptime(b, "%Y-%m-%d")
    return int((b - a).days)

def clean_dates(all_dates):
    return all_dates

def gen_dates_same_month(month):
    '''
    :param month: month to generate dates: ie "03" is march
    :return: something like [['2017-04-04', '2017-04-05'], ['2017-04-04', '2017-04-12']]
    '''
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    all_dates = []
    date = "2017-" + month + "-04"
    #dif = diff_days(date, current_date)
    if diff_days(date, current_date) <= 0: # check that today is before the departure date
        all_dates += [[date, (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=x * 7 + 1)).strftime("%Y-%m-%d")] for x in range(0, 5)]
    #if dif > 0 and dif <= 2:

    date = "2017-" + month + "-11"
    if diff_days(date, current_date) <= 0:
        all_dates += [[date, (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=x * 7 + 1)).strftime("%Y-%m-%d")] for x in range(0, 4)]

    date = "2017-" + month + "-18"
    if diff_days(date, current_date) <= 0:
        all_dates += [[date, (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=x * 7 + 1)).strftime("%Y-%m-%d")] for x in range(0, 3)]

    date = "2017-" + month + "-25"
    if diff_days(date, current_date) <= 0:
        all_dates += [[date, (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=x * 7 + 1)).strftime("%Y-%m-%d")] for x in range(0, 2)]

    return all_dates

def gen_dates_different_month(month_departure, month_return):

    '''
    Generates a list of list of dates
    :param month_departure: ie "03"
    :param month_return:  ie "04"
    :return: something like [['2017-03-04', '2017-04-04'], ['2017-04-04', '2017-05-11']]
    '''
    all_dates = []
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_departure_base = "2017-" + month_departure + "-04"
    for i in range(0, 5):
        date_departure = datetime.datetime.strptime(date_departure_base, "%Y-%m-%d") + datetime.timedelta(days=i * 7)
        date_return_base = "2017-" + month_return + "-04"
        date_departure_full = date_departure.strftime("%Y-%m-%d")
        if diff_days(date_departure_full, current_date) <= 0: # check that today is before the departure date
            all_dates += [[date_departure_full,(datetime.datetime.strptime(date_return_base, "%Y-%m-%d")
                                                            + datetime.timedelta(days=x * 7)).strftime("%Y-%m-%d")] for x in range(0, 5)]
    return all_dates

def gen_dates_no_return(month_departure):
    all_dates = []
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_departure_base = "2017-" + month_departure + "-04"
    for i in range(0, 5):
        date_departure = datetime.datetime.strptime(date_departure_base, "%Y-%m-%d") + datetime.timedelta(days=i * 7)
        date_departure_full = date_departure.strftime("%Y-%m-%d")
        if diff_days(date_departure_full, current_date) <= 0:  # check that today is before the departure date
            all_dates += [[date_departure_full, "no-return"]]
    return all_dates

def gen_dates(month_departure, month_return):
    '''
    generates the list of lists for departure and return dates
    :param month_departure: i.e "03" for march
    :param month_return: i.e "06" for june
    they have to be str of two characters
    :return: list of lists with possible departure dates and return dates in each element
    i.e [['2017-03-04', '2017-04-04'], ['2017-04-04', '2017-05-11']]
    '''
    if month_departure == month_return:
        return gen_dates_same_month(month_departure)
    if month_return == "00":
        return gen_dates_no_return(month_departure)
    else:
        return gen_dates_different_month(month_departure, month_return)


def gen_links(dates, airport_departure, airport_arrival, extensions = ["es"]):
    '''
    creates the links to scrape in the form:
    https://www.kayak.es/flights/FCO-BKK,KUL/2017-04-11-flexible/2017-07-02-flexible
    :param dates: list of lists of two elements with departure date and return date in the following form:
    [["2017-02-26","2017-05-30"], ["2017-02-26","2017-06-20"]]
    :param airport_departure: the code of the departure airport: i.e "FCO" or "LHR".
    Also it admits multiple airports at the same time: i.e "FCO,LHR"
    :param airport_arrival: code of the arrival airport i.e "BKK" or "KUL" or "BKK,KUL"
    :param extensions: list of the extensions of the kayak domains: i.e ["es", "co.uk", "it", "se"]
    :return: the list of links generated
    '''
    links = []
    for extension in extensions:
        for date in dates:
            link = "https://www.kayak." + extension + "/flights/"+ airport_departure + "-" + airport_arrival + "/" + date[0] + "-flexible/" + date[1] + "-flexible"
            if "no-return" in link:
                links.append(link[:-19])
            else:
                links.append(link)
    return links

def check_web_page(web_page):
    # check if the webpage has loaded properly
    #print(web_page)
    try:
        if len(web_page.find_all(class_="rpResultContent flexDate bothFlexDates")) == 0:
            return False
        else:
            return True
    except Exception:
        return False

def retrieve_link(link, browser):
    # sleep a bit
    #sleep(random.randint(5,15))

    try:
        browser.get(link)
    except Exception:
        # timeout no problem
        pass
    sleep(10)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    loaded = check_web_page(soup)
    if loaded == False:
            return False
    return soup

def parse_data(soup):
    non_decimal = re.compile(r'[^\d.]+')
    #[ida, vuelta, precio]
    all_dates = []
    flights = soup.find_all(class_="rpResultContent flexDate bothFlexDates")
    for flight in flights:
        data=["","",""]
        # get price:
        price = flight.find_all(class_="frpDefaultPrice")[0].text
        price = non_decimal.sub("", price)
        if len(price) > 0:
            data[2] = price
        else:
            data[2] = "99999"

        # dates like 31/05
        dates = flight.find_all(class_="frpResultDate")
        #departure
        data[0] = dates[0].text

        #return
        data[1] = dates[1].text
        # Put together
        all_dates.append(data)
    return all_dates

def create_file(filename):
    header = ["departure_date", "arrival_date","price", "airport_departure", "airport_arrival", "link"]
    with open("data/" +  filename + ".tsv", "w") as f:
        f.write("\t".join(header))
        f.write("\n")

def append_data(results, airport_departure, airport_arrival, link, filename):
    # departure date, return date, price, airport departure, airport arrival, link
    for result in results:
        row = result + [airport_departure] + [airport_arrival] + [link]
        with open("data/" +  filename + ".tsv", "a") as f:
            f.write("\t".join(row))
            f.write("\n")


def find_flights(links, airport_departure, airport_arrival, filename, browser):
    # current time
    # Analyze each link
    reload = []
    counter = 1
    for link in links:
        print("[", counter, "/", len(links), "] ", link)
        counter += 1
        # download the webpage
        web_page = retrieve_link(link, browser)
        if web_page is False:
            # The link didnt work, add them to reload
            print("No data found... added to retry")
            reload.append(link)
        else:
            results = parse_data(web_page)
            append_data(results, airport_departure, airport_arrival, link, filename)
    #Now reload the links that didn't work
    counter = 1
    reload = set(reload)

    #Keep poppinnts until all are links downloaded
    #browser.set_page_load_timeout(120)
    if len(reload) > 0:
        print("\nReloading the links that did not work")
    else:
        print("\nFinished! getting " + airport_departure + "-" + airport_arrival)
    while len(reload) > 0:
        link = reload.pop()
        print("Remaining:", len(reload) + 1, " ", link)
        counter += 1
        # download the webpage
        web_page = retrieve_link(link, browser)
        if web_page is False:
            # The link didnt work, add them to reload
            print("No data found... added to retry")
            reload.add(link)
        else:
            results = parse_data(web_page)
            append_data(results, airport_departure, airport_arrival, link, filename)


def main(argv):
    month_departure = ''
    month_return = ''
    airport_departure = ''
    airport_arrival = ''
    extension = ''
    try:
        opts, args = getopt.getopt(argv,"hd:r:a:b:e:",["month-departure=","month-return=","airport-departure=","airport-return=","extension="])
    except getopt.GetoptError:
        print ('vuelos.py -e <extension> -d <month-departure> -r <month-return> -a <airport/s-departure> -b <airport/s-return>\n i.e: vuelos.py -d 03 -r 04 -a FCO -b BKK,KUL')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('vuelos.py -e <extension> -d <month-departure> -r <month-return> -a <airport/s-departure> -b <airport/s-return>\n i.e: vuelos.py -e es,co.uk -d 03 -r 04 -a FCO -b BKK,KUL')
            sys.exit()
        elif opt in ("-d", "--month-departure"):
            month_departure = arg
        elif opt in ("-r", "--month-return"):
            month_return = arg
        elif opt in ("-a", "--airport-departure"):
            airport_departure = arg
        elif opt in ("-b", "--airport-return"):
            airport_arrival = arg
        elif opt in ("-e", "--extension"):
            extension = arg

    # Main
    current_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    create_file(filename=current_time)

    PHANTOMJS_PATH = "/usr/bin/phantomjs"
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Linux; Android 5.1.1; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36")

    browser = webdriver.PhantomJS(desired_capabilities=dcap)

    dates = gen_dates(month_departure, month_return)
    links = gen_links(dates, airport_departure, airport_arrival, extensions=extension.split(","))
    random.shuffle(links)

    # Set timeout of 15 secs to 120 works good
    timeout = 60
    browser.set_page_load_timeout(timeout)

    # look for flights
    find_flights(links, airport_departure, airport_arrival, current_time, browser)

if __name__ == "__main__":
    main(sys.argv[1:])

