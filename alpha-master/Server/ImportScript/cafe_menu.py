from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


def menu_today(spoken_sentence, command):
    

    """
    Checks the CUI cafeteria menu for the day by scraping the website for the menu
    """

    # First, need to go to the website and get the html data to scrape it
    url = "https://concordia.cafebonappetit.com/"
    req = Request(url, headers={'User=Agent': 'Mozilla/5.0'})
    htmldata = urlopen(req).read()
    soup = BeautifulSoup(htmldata, 'html.parser')

    # Once html data is acquired, need to go to specific location of menu items
    items = soup.find_all('div', {"class": "site-panel__daypart-item"})

    # Make a list of all available menu items by further narrowing where to scrape
    ns = []
    for item in items:
        n = item.find('button', {'data-js': 'site-panel__daypart-item-title'})
        ns.append(n)

    # With scraped data, get the name of the meal out of the data & add it to the daily menu
    names = []
    for n in ns:
        name = str(n.get('aria-label'))
        name = name.replace('More info about ', "")
        names.append(name)

    # Finally, add the menu items to a long list and then remove the final 2 characters to avoid TTS bugs bc grammar
    output = "Here is today's menu. "
    for name in names:
        output += name + ", "
    output = output[:-2]
    return (1, output) 

#if __name__ == "__main__":
    #print(menu_today("yes", "for"))