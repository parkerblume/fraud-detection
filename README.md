# Knights BNY Fraud Detection Challenge

## Prerequisites

* python 3.0 or greater

## To set up

1. Clone the repository
2. Create the venv: `python -m venv myenv`
3. Activate the environment by navigating the project folder then run:
    * On Windows:
    `myenv\Scripts\Activate`
    * On Linux:
    `source myenv/bin/activate`
4. Install the packages: `pip install -r requirements.txt`
5. To deactivate the environment simply type `deactivate`

## Adding new packages
Simply run `pip install package` and update the requirements with `pip freeze > requirements.txt`

## To run server
With the environment activated, run `uvicorn main:app --reload`