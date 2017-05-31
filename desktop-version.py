from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import datetime
import sys, getopt
import random

def diff_days(a,b):
    '''
    Returns the diference of days
    :param a: a date like "2017-12-30"
    :param b: the other date
    :return: difference of days as int (second - first)
    '''
    a = datetime.datetime.strptime(a, "%Y-%m-%d")
    b = datetime.datetime.strptime(b, "%Y-%m-%d")
    return int((b - a).days)

def clean_dates(all_dates):
    return all_dates

def gen_dates_same_month(month):
    '''
    generates a list of list with departure dates and return dates when the departure month and return
    month are the same.
    The pattern to generate all the dates is due to the shape of the kayak.com matrix of prices and dates
    :param month: month to generate dates: ie "03" is march (needs to have 2 digits)
    :return: list of lists with possible departure dates and return dates in each element
    i.e [['2017-04-04', '2017-04-05'], ['2017-04-04', '2017-04-12']]
    '''
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    all_dates = []
    date = "2017-" + month + "-04"
    if diff_days(date, current_date) <= 0: # check that today is before the departure date
        all_dates += [[date, (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=x * 7 + 1)).strftime("%Y-%m-%d")] for x in range(0, 5)]

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
    generates a list of list with departure dates and return dates when the departure month and return
    month are not the same.
    :param month_departure: ie "03" for march (do not write "3", it needs two digits)
    :param month_return:  ie "04"
    :return: list of lists with possible departure dates and return dates in each element
    i.e [['2017-03-04', '2017-04-04'], ['2017-04-04', '2017-05-11']]
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
    '''
    check if the webpage has the matrix of prices
    :param web_page: html code of the webpage
    :return: True if the matrix is found or False if not
    '''
    try:
        if len(web_page.find_all(class_="flexdatesmatrix")[0].find_all(class_="actionlink")) == 0:
            return False
        else:
            return True
    except Exception:
        return False

def retrieve_link(link, browser):
    '''
    Downloads the html of the link
    :param link: link of kayak: i.e:
    https://www.kayak.es/flights/FCO-BKK,KUL/2017-04-11-flexible/2017-07-02-flexible
    :param browser: selenium browser with phantomjs
    :return: the HTML code if is loaded correctly or False if not
    '''
    loaded = False
    while loaded == False:
        try:
            browser.get(link)
        except Exception:
            # timeout no problem
            pass
        soup = BeautifulSoup(browser.page_source, "html.parser")
        loaded = check_web_page(soup)
        if loaded == False:
            return False
    return soup

def parse_data(web_page):
    '''
    Parses the price matrix of the webpage
    :param web_page: the HTML code
    :return: a list of lists in the shape: [[departure_date1, return_date1, price], ...]
    '''
    all_dates = []
    table = web_page.find_all(class_="flexdatesmatrix")[0].find_all(class_="actionlink")
    for row in range(len(table)):
        data = table[row]["href"].replace("'", "").replace(")", "").replace("javascript: FilterList.flexFilterToDates(", "").replace(
            " ", "").split(sep=",")
        data[0] = data[0][:4] + "-" + data[0][4:6] + "-" + data[0][6::]
        data[1] = data[1][:4] + "-" + data[1][4:6] + "-" + data[1][6::]
        data[2] = data[2]
        all_dates.append(data)
    return all_dates

def create_file(filename):
    '''
    creates a TSV with the header shown below
    :param filename: name of the file WITHOUT extension
    :return: nothing
    '''
    header = ["departure_date", "arrival_date","price", "airport_departure", "airport_arrival", "link"]
    with open("data/" +  filename + ".tsv", "w") as f:
        f.write("\t".join(header))
        f.write("\n")

def append_data(results, airport_departure, airport_arrival, link, filename):
    '''
    Appends the data into the file filename
    :param results: list of the shape [[departure_date1, return_date1, price], ...]
    :param airport_departure: the code, like FCO
    :param airport_arrival: the code, like BKK
    :param link: link where the data was taken from
    :param filename: filename to append the data to WITHOUT extension
    :return: nothing
    '''
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
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36")
    browser = webdriver.PhantomJS(desired_capabilities=dcap)

    dates = gen_dates(month_departure, month_return)
    links = gen_links(dates, airport_departure, airport_arrival, extensions=extension.split(","))
    random.shuffle(links)

    # Set timeout of 30 secs
    timeout = 30
    browser.set_page_load_timeout(timeout)

    # look for flights
    find_flights(links, airport_departure, airport_arrival, current_time, browser)

if __name__ == "__main__":
   main(sys.argv[1:])

