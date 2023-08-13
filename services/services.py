import bs4
import requests
import aiohttp
from fake_useragent import UserAgent
import asyncio

ua = UserAgent()


async def get_list_of_dishes(dish: str) -> dict[str, str] | bool:
    async with aiohttp.ClientSession() as session:
        fake_ua = {'user-agent': ua.random}
        await asyncio.sleep(0.5)
        # cite = requests.get(f'https://eda.ru/recipesearch?q={dish.lower()}')
        cite = await session.get(f'https://eda.ru/recipesearch?q={dish.lower()}', headers=fake_ua)
        if cite.status == 200:
            bs = bs4.BeautifulSoup(await cite.text(), 'lxml')
            dishes = {}
            bs = bs.find_all('div',
                             class_='tile-list__horizontal-tile horizontal-tile js-portions-count-parent '
                                    'js-bookmark__obj',
                             limit=7)
            if bs:
                for page in bs:
                    page = page.find('h3', class_='horizontal-tile__item-title item-title')
                    title = page.text.strip().replace('\xa0', ' ').replace('«', '').replace('»', '')
                    url = page.find('a').get('href')
                    dishes[title] = url
                    # print(len(title.encode('utf-8')))
                return dishes

            return False

        return False


async def get_recipe(url: str) -> str | bool:
    async with aiohttp.ClientSession() as session:
        fake_ua = {'user-agent': ua.random}
        await asyncio.sleep(0.5)
        # cite = requests.get(f'https://eda.ru{url}')
        cite = await session.get(f'https://eda.ru{url}', headers=fake_ua)
        if cite.status == 200:
            bs = bs4.BeautifulSoup(await cite.text(), 'lxml')
            bs = bs.find_all('div', class_='emotion-7yevpr')
            if bs:
                recipe = 'Ингридиенты:\n\n'
                for ind, i in enumerate(bs, 1):
                    recipe += f'{ind}. {i.find_next("span").text} - {i.find_next("span", class_="emotion-bsdd3p").text}\n'
                recipe += '\n'

                bs = bs4.BeautifulSoup(await cite.text(), 'lxml')
                bs = bs.find_all('div', itemprop="recipeInstructions")
                for ind, i in enumerate(bs, 1):
                    i = i.find_next('span', itemprop='text').text
                    recipe += f'<b>Шаг {ind}:</b> {i}\n\n'
                return recipe

            return False

        return False
