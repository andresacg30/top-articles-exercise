import datetime
import pytest
import random
import requests
from faker import Faker
from dataclasses import dataclass, field
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


# Functions


def get_top_articles(limit):
    response = requests.get(API_URL.format(limit)).json()
    cleaned_articles = []
    for record in response["data"]:
        article = Article(**record)
        cleaned_article = clean_article_title(article=article)
        cleaned_article = clean_article_number_of_comments(article=article)
        if not cleaned_article:
            pass
        cleaned_articles.append((cleaned_article.title, cleaned_article.num_comments, cleaned_article.created_at))
    sorted_articles_by_comments = sorted(cleaned_articles, key=lambda value: value[1], reverse=True)
    sorted_articles = sorted(sorted_articles_by_comments, key=lambda value: value[2], reverse=True)
    return [article.title for _ in sorted_articles_by_comments[::limit]]


def clean_article_title(article: Article):
    if not article.title and not article.story_title:
        return
    if not article.title:
        article.title = article.story_title
    return article


def clean_article_number_of_comments(article: Article):
    if article.num_comments is None:
        article.num_comments = 0
    return article


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
        created_at=fake.date_time()
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
        }
    yield create_article


def test__get_top_articles__returns_a_list_of_string():
    response = get_top_articles(1)
    assert isinstance(response, list)


def test__get_top_articles__return__the_title_with_most_comments__when_limit_is_one(mocker, article_fixture):
    list_of_articles = [article_fixture() for _ in range(10)]
    most_comment_article = article_fixture(num_comments=20, title="Title")
    list_of_articles.append(most_comment_article)
    json_response = mocker.patch("requests.get")
    json_response.return_value.json.return_value = {"data": list_of_articles}

    response = get_top_articles(1)

    assert response == most_comment_article.title


def test__get_top_articles__return__the_title_with_most_comments_and_most_recent__when_limit_is_one(mocker, article_fixture):
    list_of_articles = [article_fixture() for _ in range(10)]
    yesterdays_date = datetime.datetime.now() - datetime.timedelta(days=1)
    todays_date = datetime.datetime.now()
    most_comment_article = article_fixture(num_comments=20, title="Title", created_at=yesterdays_date)
    most_recent_article = article_fixture(num_comments=20, title="Title Most Recent", created_at=todays_date)
    list_of_articles.append(most_comment_article)
    list_of_articles.append(most_recent_article)
    json_response = mocker.patch("requests.get")
    json_response.return_value.json.return_value = {"data": list_of_articles}

    response = get_top_articles(1)

    assert response == most_recent_article.title


def test__clean_article_title__returns_unchanged_article__when_title_exists(article_fixture):
    article = article_fixture()
    cleaned_article = clean_article_title(article=article)
    assert article == cleaned_article


def test__clean_article_title__returns_cleaned_article__when_no_title_is_present_and_story_title_is_present(article_fixture):
    article = article_fixture(title=None)
    cleaned_article = clean_article_title(article=article)
    assert article == cleaned_article


def test__clean_article_title__returns_none__when_no_title_or_story_title_is_present_in_article(article_fixture):
    article = article_fixture(title=None, story_title=None)
    cleaned_article = clean_article_title(article=article)
    assert cleaned_article == None


if __name__ == "__main__":
    print(get_top_articles(2))
