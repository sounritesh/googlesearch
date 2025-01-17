from bs4 import BeautifulSoup
from requests import get
from time import sleep

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


def _req(term, session, results, lang, start, proxies):
    for i in range(5):
        try:
            resp = session.get(
                url="https://www.google.com/search",
                headers=usr_agent,
                params=dict(
                    q=term,
                    num=results + 2,  # Prevents multiple requests
                    hl=lang,
                    start=start,
                ),
                proxies=proxies,
            )
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"ERROR: {e}\n Sleeping for 2 seconds.")
            sleep(2)
            continue
    return None


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(term, session, num_results=10, lang="en", proxy=None, advanced=False):
    # escaped_term = term.replace(' ', '+')
    escaped_term = term

    # Proxy
    proxies = None
    if proxy:
        if proxy[:5] == "https":
            proxies = {"https": proxy}
        else:
            proxies = {"http": proxy}

    # Fetch
    start = 0
    while start < num_results:
        # Send request
        resp = _req(escaped_term, session, num_results -
                    start, lang, start, proxies)

        # Parse
        if not resp:
            try:
                resp = get(
                    url="https://www.google.com/search",
                    headers=usr_agent,
                    params=dict(
                        q=term,
                        num=num_results - start + 2,  # Prevents multiple requests
                        hl=lang,
                        start=start,
                    ),
                    proxies=proxies,
                )
                resp.raise_for_status()
            except Exception as e:
                print(f"ERROR: {e}")
                break

        soup = BeautifulSoup(resp.text, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})

        if (not result_block):
            break

        for result in result_block:
            # Find link, title, description
            link = result.find('a', href=True)
            title = result.find('h3')
            description_box = result.find(
                'div', {'style': '-webkit-line-clamp:2'})
            if description_box:
                description = description_box.find('span')
                if link and title and description:
                    start += 1
                    if advanced:
                        yield SearchResult(link['href'], title.text, description.text)
                    else:
                        yield link['href']
