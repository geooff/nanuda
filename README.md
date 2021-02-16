# Nanuda

Nanuda predicts emoji to match your text using [NLP](https://en.wikipedia.org/wiki/Natural_language_processing). All this fun functionality is served in a webapp built using [FastAPI](https://fastapi.tiangolo.com/) and a __ Front end.

## Installation

1. Clone the repo to your local machine
2. Make sure you have a `model.pkl` file in your repos main directory (Feel free to ask for the latest version of the model)
3. Install the project requirements in a virtual enviroment using

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements-dev.txt
```

## Usage

```bash
uvicorn webapp.serve:app --reload
```

Navigate to your local instance of Nanuda (Hint: Default address will be `http://127.0.0.1:8000`). To interact with the API without a front-end navigate to the `/docs` path for swagger documentation.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)