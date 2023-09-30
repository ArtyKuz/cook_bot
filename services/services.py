import asyncio

import aiohttp
import bs4
from fake_useragent import UserAgent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Dish, User

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


async def add_user_in_db(user_id, username, session: AsyncSession):
    """Функция добавляет пользователя в БД"""

    user = await session.get(User, user_id)
    if not user:
        session.add(User(user_id=user_id, username=username))
        await session.commit()


async def add_dish_to_favorites(user_id, title: str, recipe: str, session: AsyncSession) -> bool:
    """Добавляет рецепт в список избранных"""
    user = await session.get(User, user_id)
    dish: Dish = await session.scalar(select(Dish).where(Dish.title == title))
    if dish:
        exists = await session.scalar(select(User).join(User.dishes).where(User.user_id == user_id,
                                                                           Dish.dish_id == dish.dish_id))
        if exists:
            return False
        user.dishes.append(dish)
        await session.commit()
        return True
    else:
        dish = Dish(title=title, recipe=recipe)
        dish.users.append(user)
        session.add(dish)
        await session.commit()
        return True


async def get_favorites_dishes(user_id, session: AsyncSession) -> dict:
    """Функция для получения списка избранных блюд пользователя"""

    dishes = await session.scalars(select(Dish).join(Dish.users).where(User.user_id == user_id))
    favorites_dishes = {str(dish.dish_id): dish.title for dish in dishes.fetchall()}

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


async def get_favorite_recipe(dish_id: str, session: AsyncSession) -> str:
    """Функция для получения текста рецепта"""

    dish: Dish = await session.scalar(select(Dish).where(Dish.dish_id == int(dish_id)))
    return dish.recipe


async def delete_recipe(user_id, dish_id: str, session: AsyncSession):
    """Функция для удаления рецепта из списка избранных"""

    user = await session.get(User, user_id)
    dish = await session.get(Dish, int(dish_id))
    user.dishes.remove(dish)
    await session.commit()


async def check_count_recipes(user_id, session: AsyncSession) -> bool:
    """Функция проверяет, имеет ли пользователь Премиум доступ
    для безлимитного добавления избранных рецептов, в ином случае
    количество избранных рецептов не может превышать 10"""

    user = await session.get(User, user_id)
    if user.premium:
        return True

    dishes = await session.execute(select(User).join(User.dishes).where(User.user_id == user_id))
    return True if len(dishes.fetchall()) < 10 else False


async def get_premium(user_id, session: AsyncSession) -> None:
    """Устанавливает Премиум статус для пользователя"""

    user = await session.get(User, user_id)
    user.premium = True
    await session.commit()