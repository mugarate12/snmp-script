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
- **[Pip](https://pypi.org/project/pip/)**
- **[paramiko](https://www.paramiko.org/)**
- **[mysql connect python](https://dev.mysql.com/doc/connector-python/en/)**
- **[mysql connector python]()**

## Installation
### only Tests:

#### Windows
install paramiko library
```bash
python -m pip install paramiko
```

#### Linux
install paramiko library
```bash
pip install paramiko
```

### Production and Tests
#### Windows:

install mysql connectors libraries
```bash
python -m pip install mysql.connector
```

```bash
python -m pip install mysql-connector-python
```

#### Linux:
install mysql connectors libraries
```bash
pip install mysql.connector
```

```bash
pip install mysql-connector-python
```

## Tests
run script to connect to SSH and insert data to local host database
```bash
python search.py
```

## Run Script
```bash
python3 localhostSearch.py
```