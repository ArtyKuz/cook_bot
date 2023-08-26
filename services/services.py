import asyncio

import aiohttp
import asyncpg.connection
import bs4
from fake_useragent import UserAgent

ua = UserAgent()


async def get_list_of_dishes(dish: str) -> dict[str: dict] | bool:
    async with aiohttp.ClientSession() as session:
        fake_ua = {'user-agent': ua.random}
        await asyncio.sleep(0.5)
        cite = await session.get(f'https://eda.ru/recipesearch?q={dish.lower()}', headers=fake_ua)
        if cite.status == 200:
            bs = bs4.BeautifulSoup(await cite.text(), 'lxml')
            dishes = {}
            titles = {}
            bs = bs.find_all('div',
                             class_='tile-list__horizontal-tile horizontal-tile js-portions-count-parent '
                                    'js-bookmark__obj',
                             limit=7)

            if bs:
                for i, page in enumerate(bs):
                    page = page.find('h3', class_='horizontal-tile__item-title item-title')
                    title = page.text.strip().replace('\xa0', ' ').replace('«', '').replace('»', '')
                    titles[str(i)] = title
                    url = page.find('a').get('href')
                    dishes[str(i)] = url
                    # print(len(title.encode('utf-8')))
                # print(dishes.keys())
                # print(len(max(dishes, key=len)))
                data = {'dishes': dishes, 'titles': titles}
                return data

            return False

        return False


async def get_recipe(url: str) -> str | bool:
    async with aiohttp.ClientSession() as session:
        fake_ua = {'user-agent': ua.random}
        await asyncio.sleep(0.5)
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


async def add_user_in_db(user_id, username, conn: asyncpg.connection.Connection):
    user = await conn.fetchval('''
    SELECT user_id FROM users WHERE user_id = $1''', user_id)
    if not user:
        await conn.execute('''
        INSERT INTO users VALUES($1, $2)''', user_id, username)


async def add_dish_to_favorites(user_id, dish, recipe, conn: asyncpg.connection.Connection) -> bool:
    dish_id = await conn.fetchval('''
    SELECT dish_id FROM dishes WHERE title = $1''', dish)
    if dish_id:
        exists = await conn.fetch('''
        SELECT * FROM favorite_dishes WHERE user_id = $1 AND dish_id = $2''', user_id, dish_id)
        if exists:
            return False
        await conn.execute('''
        INSERT INTO favorite_dishes VALUES($1, $2)''', user_id, dish_id)
        return True
    else:
        dish_id = await conn.fetchval('''
        INSERT INTO dishes(title, recipe) VALUES($1, $2) RETURNING dish_id''', dish, recipe)
        await conn.execute('''
        INSERT INTO favorite_dishes VALUES($1, $2)''', user_id, dish_id)
        return True


async def get_favorites_dishes(user_id, conn: asyncpg.connection.Connection) -> dict:
    favorites_dishes = await conn.fetch('''
    SELECT dish_id, title FROM favorite_dishes JOIN dishes USING(dish_id) WHERE user_id = $1''', user_id)
    return {str(dish['dish_id']): dish['title'] for dish in favorites_dishes}


async def get_favorite_recipe(dish_id, conn: asyncpg.connection.Connection) -> str:
    recipe = await conn.fetchval('''
    SELECT recipe FROM dishes WHERE dish_id = $1''', int(dish_id))
    return recipe


async def delete_recipe(user_id, data: dict, conn: asyncpg.connection.Connection) -> dict:
    await conn.execute('''
    DELETE FROM favorite_dishes WHERE user_id = $1 AND dish_id = $2''', user_id, int(data['favorite_dish_id']))
    del data['favorites_dishes'][data['favorite_dish_id']]
    return data


