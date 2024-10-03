# Top Articles Exercise

This repository contains a function `get_top_articles` that retrieves the top articles from an API. The function takes an integer `LIMIT` as input, which determines the number of records to return. The output is a list of article titles, sorted first by the number of comments and then by the creation date. If an article does not have a title, it uses the `story_title`. If neither exists, the record is ignored.

## Requirements

- Python installed

## Setup Instructions

1. Clone the repository:
    ```sh
    git clone /Users/andrescabrera/Documents/leadconex/repos/industryp/top-articles-exercise
    cd top-articles-exercise
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On macOS and Linux:
        ```sh
        source venv/bin/activate
        ```
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```

4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Code

To run the code, use the following command:
```sh
make run
```
You will be prompted to enter the `LIMIT` in the console.

## Running Tests

To run all tests, use:
```sh
make tests
```

To run a specific test, use:
```sh
make test name=<test_name>
```

Replace `<test_name>` with the name of the test you want to run.
