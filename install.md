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

Clone the eudi-srv-web-walletdriven-signer-relyingparty-py repository from GitHub:

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

Copy \_config.py to config.py in the app_config directory and modify the following configuration variables:

- **secret_key**: Define a secure and random key

- **jwt_private_key_path**: Path to the private key file used for signing JWTs. 
- **jwt_private_key_passphrase**: Passphrase for the private key (if applicable).
- **jwt_certificate_path**: Path to the JWT certificate file.
- **jwt_ca_certificate_path**: Path to the CA certificate file.
- **jwt_algorithm**: Algorithm used to generate JWTs.

- **service_domain**: Define the service domain.
- **wallet_url**: URL of the wallet app endpoint for signature requests.
- **pre_registered_client_id**: Pre-registered client ID for signature requests to the wallet.

- **db_name**: Name of the database.
- **db_user**: Database username.
- **db_password**: Database user password.

The \_config.py template supports loading configuration values from environment variables using the os.getenv() function. 
This is especially useful when deploying the app using docker-compose, where environment variables can be defined in the docker-compose.yml or a .env file.

### Step 7: Set up the Database:

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

4. **Update config.py**

    Add the following parameters to the 'config.py' in the 'app_config' directory:
    
    ```
    db_host = 'localhost'
    db_port = '3306'
    db_name = {db_name}
    db_user = {db_user}
    db_password = {db_password}
    ```

   * **Docker Deployment Notes**
   When using Docker Compose, you should define the database credentials as environment variables instead of hardcoding them. 
   Here's an example snippet from a 'docker-compose.yml' file:
   ```
   environment:
      DB_NAME: {db_name}
      DB_USER: {db_user}
      DB_PASSWORD: {db_password}
   ```
   In Docker environments, set db_host in the config.py to "host.docker.internal" to allow the container to access services running on the host machine.
   Otherwise, use "localhost" for local (non-containerized) development.

### Step 8: Create a Key Pair and a Certificate

Use OpenSSL to generate a private key and a certificate signing request:
```
openssl genpkey -genparam -algorithm ec -pkeyopt ec_paramgen_curve:P-256 -out ECPARAM.pem
openssl req -newkey ec:ECPARAM.pem -keyout PRIVATEKEY.key -out MYCSR.csr -config csr.conf
```

Before executing these commands, create a configuration file named **csr.conf** with the following structure:
```
[req]
distinguished_name = dn
prompt             = no
req_extensions = req_ext

[dn]
C={country}
CN={common_name_rp}

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.0 = {domain_name}
```

Ensure that certificates retrieved from the Certification Authority (CA) are in **.cer** format. You can convert a certificate using:
```
openssl x509 -inform PEM -in {file_name}.pem -outform DER -out {filename}.cer
```

Submit the certificate signing request (MYCSR.csr) to a Certification Authority. 
Once issued, update **config.py** with the appropriate paths:
- **jwt_private_key_path**: Path to the private key file.
- **jwt_private_key_password**: Passphrase for the private key (if applicable).
- **jwt_certificate_path**: Path to the issued certificate file.
- **jwt_ca_certificate_path**: Path to the CA certificate file.
- **jwt_algorithm**: Algorithm used to generate JWTs.

* **Docker Deployment Notes**

When deploying with Docker, define the necessary environment variables in your 'docker-compose.yml':
```
environment:
   JWT_PRIVATE_KEY_PATH: "/app/certificates/..."
   JWT_PRIVATE_KEY_PASSWORD: "private key password"
   JWT_CERTIFICATE_PATH: "/app/certificates/..."
   JWT_CA_CERTIFICATE_PATH: "/app/certificates/..."
volumes:
   - certificates/:/app/certificates/
```
This setup maps your local 'certificates/' folder into the container and provides the containerized application access to your JWT keys and certificates.

### Step 9: Create a Logs Folder

Create a **logs** folder inside **eudi-srv-web-walletdriven-signer-relyingparty-py**.

### Step 10: Run the Application

Run the EUDI Wallet-Driven Relying Party application (on <http://127.0.0.1:5000>)

```shell
flask --app app run
```
