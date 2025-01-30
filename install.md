# Installation

## 1. Python

The EUDI Wallet-Driven Relying Party application was tested with

- Python version 3.10.12

and should only be used with Python 3.10 or higher.

If you don't have it installed, please downlod it from <https://www.python.org/downloads/> and follow the [Python Developer's Guide](https://devguide.python.org/getting-started/).

## 2. Flask

The EUDI Wallet-Driven Relying Party application was tested with

- Flask v. 2.3

and should only be used with Flask v. 2.3 or higher.

To install [Flask](https://flask.palletsprojects.com/en/2.3.x/), please follow the [Installation Guide](https://flask.palletsprojects.com/en/2.3.x/installation/).

## 3. Running the EUDI Wallet-Driven Relying Party Application

To run the application, follow these simple steps (some of which may have already been completed when installing Flask) for Linux/macOS or Windows.

### Step 1: Clone the Repository

Clone the eudi-srv-web-rpcentric-signer-relyingparty-py repository from GitHub:

```shell
git clone git@github.com:eu-digital-identity-wallet/eudi-srv-web-walletdriven-signer-relyingparty-py.git
```

### Step 2: Create a Virtual Environment

Create a `.venv` folder within the cloned repository:

```shell
cd eudi-srv-web-walletdriven-signer-relyingparty-py
python3 -m venv .venv
```

### Step 3: Activate the Virtual Environment

Linux/macOS

```shell
. .venv/bin/activate
```

Windows

```shell
. .venv\Scripts\Activate
```

### Step 4: Upgrade pip

Install or upgrade _pip_

```shell
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies

Install Flask and other dependencies in virtual environment

```shell
pip install -r app/requirements.txt
```

### Step 6: Configure the Application

Copy \_config.py to config.py and modify the following configuration variables:

- **secret_key**: define a secure and random key
- **jwt_secret**: define a secure and random key used to generate a JWT
- **jwt_algorithm**: define an algorithm to generate a JWT
- **service_url**: the base URL of the service
- **wallet_url**: the URL of the wallet app's endpoint where the signature request is made

### Step 7: Run the Application

Run the EUDI RP-Centric Relying Party application (on <http://127.0.0.1:5000>)

```shell
flask --app app run
```
