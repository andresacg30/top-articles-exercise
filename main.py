import datetime
import pytest
import random
import requests
from faker import Faker
from dataclasses import dataclass
from typing import Optional


API_URL = "https://jsonmock.hackerrank.com/api/articles?page={}"


# Models

@dataclass
class Article:
    url: str
    author: str
    num_comments: int
    title: Optional[str]
    story_id: Optional[int]
    story_title: Optional[str]
    story_url: Optional[str]
    parent_id: Optional[int]
    created_at: datetime.datetime
    comment_text: Optional[str] = None

    def __post_init__(self):
        self.clean_article_number_of_comments()

    def clean_article_number_of_comments(self):
        if self.num_comments is None:
            self.num_comments = 0


# Functions


def get_top_articles(limit):
    articles = get_all_articles(limit=limit)
    cleaned_articles_tuples = []
    for record in articles:
        article = Article(**record)
        cleaned_article = clean_article_title(article=article)
        if not cleaned_article:
            continue
        cleaned_articles_tuples.append((cleaned_article.title, cleaned_article.num_comments, cleaned_article.created_at))
    sorted_articles = sort_articles(cleaned_articles_tuples)
    return [article[0] for article in sorted_articles[:limit]]


def clean_article_title(article: Article):
    if not article.title and not article.story_title:
        return
    if not article.title:
        article.title = article.story_title
    return article


def sort_articles(articles):
    sorted_articles_by_comments = sorted(articles, key=lambda value: value[1], reverse=True)
    sorted_articles = sorted(sorted_articles_by_comments, key=lambda value: value[2], reverse=True)
    return sorted_articles


def get_all_articles(limit):
    articles = []
    page = 1

    while len(articles) < limit:
        response = requests.get(API_URL.format(page)).json()
        if limit > response["total"]:
            limit = response["total"]
        articles.extend(response["data"])
        page += 1
        if page > response["total_pages"]:
            break

    return articles


# Tests

fake = Faker()


@pytest.fixture
def article_fixture():
    def create_article(
        url=fake.url(),
        author=fake.name(),
        num_comments=random.randint(1, 10),
        title=fake.sentences(1)[0],
        story_id=fake.uuid4(),
        story_title=fake.sentences(1)[0],
        story_url=fake.url(),
        parent_id=fake.uuid4(),
        created_at=fake.date_time(),
        comment_text=fake.sentences(1)[0],
    ):
        return {
            "url": url,
            "author": author,
            "num_comments": num_comments,
            "title": title,
            "story_id": story_id,
            "story_title": story_title,
            "story_url": story_url,
            "parent_id": parent_id,
            "created_at": created_at,
            "comment_text": comment_text,
        }
    yield create_article


def test__get_top_articles__returns_a_list_of_string():
    response = get_top_articles(1)
    assert isinstance(response, list)
    assert all(isinstance(article, str) for article in response)


def test__clean_article_title__returns_unchanged_article__when_title_exists(article_fixture):
    article_dict = article_fixture()
    article = Article(**article_dict)

    cleaned_article = clean_article_title(article=article)

    assert article == cleaned_article


def test__clean_article_title__returns_cleaned_article__when_no_title_is_present_and_story_title_is_present(article_fixture):
    article_dict = article_fixture(title=None)
    article = Article(**article_dict)

    cleaned_article = clean_article_title(article=article)

    assert article == cleaned_article


def test__clean_article_title__returns_none__when_no_title_or_story_title_is_present_in_article(article_fixture):
    article_dict = article_fixture(title=None, story_title=None)
    article = Article(**article_dict)

    cleaned_article = clean_article_title(article=article)

    assert cleaned_article is None


def test__sort_articles__returns_sorted_articles_by_comments(article_fixture):
    articles = [article_fixture() for _ in range(10)]
    articles_tuple = [(article["title"], article["num_comments"], article["created_at"]) for article in articles]

    sorted_articles = sort_articles(articles_tuple)

    assert sorted_articles == sorted(articles_tuple, key=lambda value: value[1], reverse=True)


def test__sort_articles__returns_sorted_articles_by_created_at(article_fixture):
    articles = [article_fixture() for _ in range(10)]
    articles_tuple = [(article["title"], article["num_comments"], article["created_at"]) for article in articles]

    sorted_articles = sort_articles(articles_tuple)

    assert sorted_articles == sorted(articles_tuple, key=lambda value: value[2], reverse=True)


def test__get_all_articles__returns_list_of_article_titles__when_limit_is_10():
    articles = get_all_articles(10)

    assert isinstance(articles, list)
    assert all(isinstance(article, dict) for article in articles)
    assert len(articles) == 10


def test__get_all_articles__returns_list_of_article_titles__when_limit_is_api_max():
    total = requests.get(API_URL.format(1)).json()["total"]

    articles = get_all_articles(total)

    assert isinstance(articles, list)
    assert all(isinstance(article, dict) for article in articles)
    assert len(articles) == total


def test__get_top_articles__returns_list_of_article_titles__when_limit_is_10():
    articles = get_top_articles(10)
    assert isinstance(articles, list)
    assert all(isinstance(article, str) for article in articles)
    assert len(articles) == 10


def test__get_top_article_titles__returns_list_of_article_titles__when_limit_is_api_max():
    total = requests.get(API_URL.format(1)).json()["total"]
    articles = get_all_articles(limit=total)
    ignored_articles = sum(1 for article in articles if not clean_article_title(Article(**article)))

    articles = get_top_articles(total)

    assert isinstance(articles, list)
    assert all(isinstance(article, str) for article in articles)
    assert len(articles) == (total - ignored_articles)


def test__get_top_article_titles__returns_list_of_article_titles__when_limit_is_0():
    articles = get_top_articles(0)
    assert isinstance(articles, list)
    assert all(isinstance(article, str) for article in articles)
    assert len(articles) == 0


def test__get_top_articles__returns_list_of_article_titles__when_limit_is_greater_than_api_max():
    total = requests.get(API_URL.format(1)).json()["total"]
    articles = get_all_articles(limit=total)
    ignored_articles = sum(1 for article in articles if not clean_article_title(Article(**article)))

    articles = get_top_articles(total + 1)

    assert isinstance(articles, list)
    assert all(isinstance(article, str) for article in articles)
    assert len(articles) == (total - ignored_articles)


if __name__ == "__main__":
    print(get_top_articles(int(input("Enter the number of article titles you want to retrieve: "))))
