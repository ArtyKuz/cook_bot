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


async def get_recipe(url: str, name_dish: str) -> str | bool:
    async with aiohttp.ClientSession() as session:
        fake_ua = {'user-agent': ua.random}
        await asyncio.sleep(0.5)
        cite = await session.get(f'https://eda.ru{url}', headers=fake_ua)
        if cite.status == 200:
            bs = bs4.BeautifulSoup(await cite.text(), 'lxml')
            bs = bs.find_all('div', class_='emotion-7yevpr')
            if bs:
                recipe = f'<b>{name_dish}</b>\n\nИнгридиенты:\n\n'
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
    """Функция добавляет пользователя в БД"""

    user = await conn.fetchval('''
    SELECT user_id FROM users WHERE user_id = $1''', user_id)
    if not user:
        await conn.execute('''
        INSERT INTO users VALUES($1, $2)''', user_id, username)


async def add_dish_to_favorites(user_id, dish, recipe, conn: asyncpg.connection.Connection) -> bool:
    """Функция """

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
    """Функция для получения списка избранных блюд пользователя"""

    favorites_dishes = await conn.fetch('''
    SELECT dish_id, title FROM favorite_dishes JOIN dishes USING(dish_id) WHERE user_id = $1''', user_id)
    favorites_dishes = {str(dish['dish_id']): dish['title'] for dish in favorites_dishes}
    pagination = {}
    page = '1'
    pagination[page] = []
    for i in favorites_dishes.items():
        if len(pagination[page]) < 5:
            pagination[page].append(i)
        else:
            page = str(int(page) + 1)
            pagination[page] = [i]
    return pagination


async def get_favorite_recipe(dish_id, conn: asyncpg.connection.Connection) -> str:
    """Функция для получения текста рецепта"""

    recipe = await conn.fetchval('''
    SELECT recipe FROM dishes WHERE dish_id = $1''', int(dish_id))
    return recipe


async def delete_recipe(user_id, data: dict, conn: asyncpg.connection.Connection) -> dict:
    """Функция для удаления рецепта из списка избранных"""

    await conn.execute('''
        DELETE FROM favorite_dishes WHERE user_id = $1 AND dish_id = $2''', user_id, int(data['favorite_dish_id']))


async def check_count_recipes(user_id, conn: asyncpg.connection.Connection) -> bool:
    """Функция проверяет, имеет ли пользователь Премиум доступ
    для безлимитного добавления избранных рецептов, в ином случае
    количество избранных рецептов не может превышать 10"""

    result = await conn.fetchval('''
    SELECT premium FROM users WHERE user_id = $1''', user_id)
    if result:
        return True
    else:
        count = await conn.fetchval('''
        SELECT count(*) FROM favorite_dishes WHERE user_id = $1''', user_id)
        return True if count < 10 else False


async def get_premium(user_id, conn: asyncpg.connection.Connection) -> None:
    """Устанавливает Премиум статус для пользователя"""

    await conn.execute('''
    UPDATE users SET premium = True WHERE user_id = $1''', user_id)
