# Installation

## Prerequisites

### Set up the Database

1. **Create database with {db_name}**

    ```
    CREATE DATABASE {db_name};
    ```

2. **Create a database user**

    ```
    CREATE USER {db_user}@'localhost' IDENTIFIED BY {db_password};
    GRANT ALL PRIVILEGES ON {db_name}.* TO {db_user}@'localhost';
    ```

3. **Create required database tables**

    ```
    use {db_name};
    create table sd (request_id varchar(255), request_object text);
    create table sdo (id int NOT NULL AUTO_INCREMENT, request_id varchar(255), signed_data_object mediumtext, error varchar(255), PRIMARY KEY (id));
    ```

4. **Alternative: Run MySQL Database Script**
    
    A script containing the above SQL commands is available in the `tools` folder. Update the parameters 'db_name', 'db_username' and 'db_user_password' in the script and run the command:
    ```shell
    sudo mysql < tools/db_create.sql
    ```

5. **Save the configuration parameters**

    Store the values used above (e.g., database name, user, and password) for use during the main project setup.  
    You can update them in either:
    
    - the `config.py` file under the `app_config` directory, or  
    - the `.env` file.

### Register Relying Party and Retrieve Key Pair and Certificate

To ensure the correct functionality of the **rQES Wallet-Driven Relying Party**, you must register the Relying Party in 
the [Testing Relying Party Registration](https://registry.serviceproviders.eudiw.dev/).

**Important:** Make sure that the DNS Name defined during registration matches the domain of your Relying Party exactly.

Use the following commands to extract the certificate and private key from a .p12 file returned by the *Testing Relying Party Registration*:
```shell
# Extract certificate in PEM format
openssl pkcs12 -in {p12 file} -nodes -nokeys -out RP_CERT.crt

# Convert PEM certificate to DER format (optional)
openssl x509 -in RP_CERT.crt -out RP_CERT.cer -outform DER

# Extract private key
openssl pkcs12 -in {p12 file} -nodes -nocerts -out sk.key
```

Once retrieved, update **config.py** file or the **.env** file with the appropriate paths and settings:
- **jwt_private_key_path**: Path to the private key file.
- **jwt_private_key_password**: Passphrase for the private key (if applicable).
- **jwt_certificate_path**: Path to the issued certificate file.
- **jwt_ca_certificate_path**: Path to the CA certificate file.

## Local Deployment

### 1. Python

The EUDI Wallet-Driven Relying Party application was tested with

- Python version 3.10.12

and should only be used with Python 3.10 or higher.

If you don't have it installed, please downlod it from <https://www.python.org/downloads/> and follow the [Python Developer's Guide](https://devguide.python.org/getting-started/).

### 2. Flask

The EUDI Wallet-Driven Relying Party application was tested with

- Flask v. 2.3

and should only be used with Flask v. 2.3 or higher.

To install [Flask](https://flask.palletsprojects.com/en/2.3.x/), please follow the [Installation Guide](https://flask.palletsprojects.com/en/2.3.x/installation/).

### 3. Running the EUDI Wallet-Driven Relying Party Application

To run the application, follow these simple steps (some of which may have already been completed when installing Flask) for Linux/macOS or Windows.

#### Step 1: Clone the Repository

Clone the eudi-srv-web-walletdriven-signer-relyingparty-py repository from GitHub:

```shell
git clone git@github.com:eu-digital-identity-wallet/eudi-srv-web-walletdriven-signer-relyingparty-py.git
```

#### Step 2: Create a Virtual Environment

Create a `.venv` folder within the cloned repository:

```shell
cd eudi-srv-web-walletdriven-signer-relyingparty-py
python3 -m venv .venv
```

#### Step 3: Activate the Virtual Environment

Linux/macOS

```shell
. .venv/bin/activate
```

Windows

```shell
. .venv\Scripts\Activate
```

#### Step 4: Upgrade pip

Install or upgrade _pip_

```shell
python -m pip install --upgrade pip
```

#### Step 5: Install Dependencies

Install Flask and other dependencies in virtual environment

```shell
pip install -r app/requirements.txt
```

#### Step 6: Configure the Application

Update the **config.py** file located in the app_config directory or, alternatively, create an **.env** file. In either case, configure the following variables:

- **secret_key**: A secure, random secret key used for session management and signing.
- **jwt_private_key_path**: Path to the private key file used for signing JWTs. (See: [Register Relying Party and Retrieve Key Pair and Certificate](#register-relying-party-and-retrieve-key-pair-and-certificate))
- **jwt_private_key_passphrase**: Passphrase for the private key (if applicable). (See same reference as above.)
- **jwt_certificate_path**: Path to the JWT certificate file. (See same reference as above.)
- **jwt_ca_certificate_path**: Path to the CA certificate file. (See same reference as above.)
- **service_domain**: The domain or DNS name of your service.
- **wallet_url**: URL of the wallet app endpoint for signature requests.
- **pre_registered_client_id**: Client ID pre-registered for interactions with the wallet.
- **db_host**: Database host (e.g., localhost).
- **db_port**: Database port (e.g., 3306).
- **db_name**: Name of the database. (See: [Set up the Database](#set-up-the-database))
- **db_user**: Username for accessing the database. (See same reference as above.)
- **db_password**: Password for the database user. (See same reference as above.)

You may alternatively define all variables in a *.env* file:

```
FLASK_RUN_PORT=            # Port where the Relying Party is running
SECRET_KEY=                # Define a secure and random key
JWT_PRIVATE_KEY_PATH=
JWT_PRIVATE_KEY_PASSWORD=
JWT_CERTIFICATE_PATH=
JWT_CA_CERTIFICATE_PATH=
SERVICE_DOMAIN= 127.0.0.1:5001
SERVICE_URL= http://127.0.0.1:5001/rp
WALLET_URL=
DB_HOST=localhost
DB_PORT=3306
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
```

#### Step 7: Run the Application

Run the EUDI Wallet-Driven Relying Party application (on <http://127.0.0.1:5001>)

```shell
flask --app app run --port 5001
```

## Docker Deployment

You can also deploy the Wallet-Driven Relying Party using Docker in two ways:

- Use the pre-built image from GitHub Container Registry
- Build the Docker image locally from source

Note: Don't forget to follow the [Prerequisites](#Prerequisites).

### Requirements

- Docker
- Docker Compose

### Configure .env File

Create a *.env* file in the project root with the following structure:
```shell
FLASK_RUN_PORT= # Port for the Flask server 
SECRET_KEY= # A secure and random key
JWT_PRIVATE_KEY_PATH= # Path inside container
JWT_PRIVATE_KEY_PASSWORD= 
JWT_CERTIFICATE_PATH= # Path inside container
JWT_CA_CERTIFICATE_PATH= # Path inside container
SERVICE_DOMAIN= 127.0.0.1:5001
SERVICE_URL=http://127.0.0.1:5001/rp
WALLET_URL= # URL for a Wallet Tester
DB_HOST=host.docker.internal  # Use 'host.docker.internal' to access host from container
DB_PORT=3306
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
```

See the section [Step 6: Configure the Application](#step-6-configure-the-application) for more details about the configuration parameters.

### Configure docker-compose.yml

#### Use Pre-Built Image

To use the pre-built image from GitHub, modify your docker-compose.yml as follows:

```
services:
  walletdriven_relyingparty:
    image: ghcr.io/eu-digital-identity-wallet/eudi-srv-web-walletdriven-signer-relyingparty-py:latest
    container_name: walletdriven_relyingparty
    ...
```

#### Configure Certificate Volume

Ensure the container can access your key and certificate files by mounting the correct volume:

```
volumes:
   - ./certificates/:/app/certificates/
```
This maps your local ./certificates/ directory into the container's /app/certificates/ path.

Make sure the files created during [Register Relying Party and Retrieve Key Pair and Certificate](#register-relying-party-and-retrieve-key-pair-and-certificate) are present in this directory.

**Optional**: To avoid port conflicts, change the exposed port:

```
ports:
    - "5001:5001" # Change first 5001 if the port is already used
```

### Build and Run with Docker

To start the 'EUDI Wallet-Driven Relying Party' application as a Docker Container, run the command:
```shell
docker compose up --build
```