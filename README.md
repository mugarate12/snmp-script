# SNMP script

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Tests](#tests)
- [Run Script](#run-script)

## Overview
script to get informations, run this script in your local machine and this connect to ssh and run commands to filter results

## Requirements

- **[Python](https://www.python.org/)** (supported versions: 3.9.x)
- **[paramiko](https://www.paramiko.org/)**
- **[mysql connect python](https://dev.mysql.com/doc/connector-python/en/)**
- **[mysql connector python]

## Installation
install paramiko library
```bash
python -m pip install paramiko
```

install mysql connectors libraries
```bash
python -m pip install mysql.connector
```

```bash
python -m pip install mysql-connector-python
```

## Tests
run script to connect to SSH and insert data to local host database
```bash
python search.py
```

## Run Script
```bash
python localhostSearch.py
```