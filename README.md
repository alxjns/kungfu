# kungfu
Kung Fu heplps you turn your OpenAPI spec into Karate tests. 

It outputs JSON with [Karate fuzzy matchers](https://github.com/intuit/karate#fuzzy-matching) corresponding to a compiled JSON spec file or individual YAML schema files. These output JSON files can be used in your Karate tests to quickly validate the structure of API response bodies.

For example, an output `CreditCard.json` might look like:

    {
        "type": "#regex(credit\\-card)",
        "nameOnCard": "#string",
        "cardNumber": "#string",
        "cardType": "#regex(amex|discover|mastercard|visa)",
        "expirationMonth": "#number",
        "expirationYear": "#number",
        "postCode": "##string"
    }

## Environment setup
* Clone the repo
* Install Python
* Optionally, create and activate a Python `virtualenv`
* Run `pip install -r requirements.txt` to download dependencies

## Running the scripts
Run `loadfiles.py` with Python, passing command line arguments.

It must be passed a file or folder where the OpenAPI files are located

    python loadfiles.py ~/path/to/docs.json

It optionally accepts an output location

    python loadfiles.py ~path/to/docs/ --out outputFolder
