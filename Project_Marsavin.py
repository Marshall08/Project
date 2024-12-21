import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import streamlit as st

def fetch_github_data(query="stars:>10000", per_page=100, pages=3):
    base_url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github.v3+json"}
    repos = []
    for page in range(1, pages + 1):
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page, "page": page}
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            repos.extend(response.json()["items"])
    return pd.DataFrame(repos)

def fetch_stack_overflow(language="Python"):
    base_url = f"https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": language,
        "site": "stackoverflow",
        "pagesize": 50
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()["items"]
        return pd.DataFrame({
            "title": [item["title"] for item in data],
            "score": [item["score"] for item in data],
            "link": [item["link"] for item in data]
        })
    return pd.DataFrame({"Error": ["Unable to fetch data from Stack Overflow."]})

def fetch_github_trending():
    url = "https://github.com/trending"
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame({"Error": ["Unable to fetch GitHub trending data."]})

    soup = BeautifulSoup(response.text, "html.parser")
    repos = soup.find_all("article", class_="Box-row")
    if not repos:
        return pd.DataFrame({"Error": ["No trending repositories found on GitHub."]})

    data = []
    for repo in repos[:10]:
        name_tag = repo.find("h2", class_="h3 lh-condensed")
        name = name_tag.text.strip() if name_tag else "No name"
        description_tag = repo.find("p", class_="col-9 color-fg-muted my-1 pr-4")
        description = description_tag.text.strip() if description_tag else "No description"
        data.append({"repository": name, "description": description})
    return pd.DataFrame(data)

st.title("Проект по анализу популярных технологий и репозиториев")
st.write("Проект анализирует репозитории GitHub и Stack Overflow.")

st.header("Популярные репозитории GitHub")
github_data = fetch_github_data()
st.write("Топ 10 популярных репозиториев:")
st.dataframe(github_data[["name", "stargazers_count", "html_url"]].head(10))

fig_github = px.bar(
    github_data.head(10), 
    x="name", 
    y="stargazers_count", 
    title="Топ 10 репозиториев по звёздам", 
    text="stargazers_count"
)
st.plotly_chart(fig_github)

st.header("Популярные вопросы на Stack Overflow")
language = st.text_input("Введите язык программирования:", "Python")
stack_overflow_data = fetch_stack_overflow(language)
if "Error" in stack_overflow_data.columns:
    st.error("Ошибка при загрузке данных с Stack Overflow: " + stack_overflow_data["Error"].iloc[0])
else:
    st.write(f"Топ 5 вопросов по {language}:")
    st.dataframe(stack_overflow_data[["title", "score", "link"]].head(5))

st.header("Тренды GitHub")
trending_data = fetch_github_trending()
if "Error" in trending_data.columns:
    st.error("Ошибка при загрузке данных с GitHub Trending: " + trending_data["Error"].iloc[0])
else:
    st.write("Топ 5 трендов GitHub:")
    st.dataframe(trending_data.head(5))

st.header("Выводы")
st.markdown("""
- **GitHub:** Наиболее популярны репозитории с большим количеством звёзд, такие как React.
- **Stack Overflow:** Вопросы с высоким рейтингом показывают проблемы сообщества разработчиков.
- **GitHub Trending:** Трендовые репозитории показывают актуальные темы для исследований.
""")
