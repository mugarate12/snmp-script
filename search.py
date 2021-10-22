# from paramiko import SSHClient
import paramiko
import mariadb

# database informations
database_host = 'localhost'
database_user= 'root'
database_password= 'majuge123'
database_port = 3307

# host connection
host = "138.0.233.24"
port = 22
username = "ora"
password = "oRa@#t3lecom"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

community = 'W1r3l1nk'
ip = '172.31.3.106'
oids = 'iso.3.6.1.4.1.2011.5.25.191.2.1.1.8'

gadgets = [
  {
    'equipamento': 'Fran',
    'community': 'W1r3l1nk',
    'ip': '172.31.3.106'
  }
]

def getID(searchResult, oids):
  """
  get id of a line to snmp
  """
  index = searchResult.split('=')[0]
  indexNumber = index[len(oids) + 1 : len(index)]

  return int(indexNumber)

def getPeer(searchResult):
  """
  get peer number of result
  """
  stringAfterPeer = searchResult.split('peer ')[1]
  peer = stringAfterPeer.split(' ')[0]

  return peer

def getContent(searchResult, filterString):
  """
  get result of searchResult
  """
  stringAfterFilter = searchResult.split(f'{filterString} ')[1]
  content = stringAfterFilter[0: len(stringAfterFilter) - 2]

  return content

def getInformations(searchResult, filterString):
  """
  get informations of a line to snmp search
  """
  searchID = getID(searchResult, oids)
  peer = getPeer(searchResult)
  content = getContent(searchResult, filterString)

  # print(f'{filterString}\nid: {searchID}\npeer: {peer}\ncontent: {content}\n')

  return {
    'id': searchID,
    'peer': peer,
    'content': content
  }

def runFilter(command, filter):
  """
  
  """
  filter = f'{command} | grep {filter}'
  stdin, stdout, stderr = ssh.exec_command(filter)
  searchResult = stdout.readlines()

  return searchResult

def searchWithPeer(peer, arraySearch):
  for search in arraySearch:
    if peer in search:
      return search

def informationPerPeer(descriptionArraySearch, asNumberArraySearch, connectInterfaceArraySearch):
  informations = []

  for descriptionSearch in descriptionArraySearch:
    peer = getPeer(descriptionSearch)

    descriptionToPeer = searchWithPeer(peer, descriptionArraySearch)
    informatonsDescription = getInformations(descriptionToPeer, 'description')

    asNumberToPeer = searchWithPeer(peer, asNumberArraySearch)
    informationsAsNumber = getInformations(asNumberToPeer, 'as-number')

    connectInterfaceToPeer = searchWithPeer(peer, connectInterfaceArraySearch)
    informationsConnectInterface = getInformations(connectInterfaceToPeer, 'connect-interface')

    information = {
      'description': informatonsDescription,
      'as-number': informationsAsNumber,
      'connect-interface': informationsConnectInterface
    }

    informations.append(information)
  
  return informations
  
def runRoutine(command):
  descriptionSearch = runFilter(command, 'description')
  asNumberSearch = runFilter(command, 'as-number')
  connectInterfaceSearch = runFilter(command, 'connect-interface')

  return informationPerPeer(descriptionSearch, asNumberSearch, connectInterfaceSearch)

def createDatabase(cursor, databaseName):
  """
  create database to insert data of gadgets
  """
  cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")
  cursor.execute(f"use {databaseName}")

def createTable(cursor, tableName):
  """
  create table to insert peer informations of gadget
  """
  createTable = f"""CREATE TABLE IF NOT EXISTS {tableName} 
                    (id                 int not null auto_increment primary key,
                    equipamento         varchar(200),
                    ip                  varchar(200),
                    peer                varchar(200),
                    as_number           varchar(200),
                    description         varchar(200),
                    connect_interface   varchar(200));
             """
  cursor.execute(createTable)

def alterTable(cursor, tableName):
  """
  alter table to modify 'equipamento' field from int to varchar(200)
  """
  alterTableQuery = f"""ALTER TABLE {tableName}
                        MODIFY equipamento varchar(200);
                  """
  cursor.execute(alterTableQuery)

def getRegistry(cursor, tableName, ip, peer):
  """
  get registry of gadget with ip and peer
  """
  verifyExistsRegistry = f""" SELECT * from {tableName}
                              WHERE ip='{ip}' and peer='{peer}';
                            """
  cursor.execute(verifyExistsRegistry)
  registry = cursor.fetchone()

  return registry

def createRegistry(conn, cursor, tableName, gadgetName, ip, peer, asNumber, description, connectInterface):
  """
  create information of gadget peer
  """
  createItem = f"""INSERT INTO {tableName}
                      (equipamento, ip, peer, as_number, description, connect_interface) 
                    VALUES
                      ("{gadgetName}", "{ip}", "{peer}", "{asNumber}", "{description}", "{connectInterface}");
                  """
  cursor.execute(createItem)
  conn.commit()

def runCommands():
  """
  run three comands to get informations
  """

  for gadget in gadgets:
    command = f'snmpwalk -v2c -c {gadget["community"]} {gadget["ip"]} iso.3.6.1.4.1.2011.5.25.191.2.1.1.8 | grep peer'
    
    informations = runRoutine(command)
    # print(informations)

    databaseName = 'sw_hws6730'
    tableName = 'equipamentos'

    try:
      conn = mariadb.connect(
        user=database_user,
        password=database_password,
        host=database_host,
        port=database_port
      )
      print('connection with database ok')
    except mariadb.Error as err:
        print(err)
    else:
        cursor = conn.cursor()
      
    createDatabase(cursor, databaseName)

    createTable(cursor, tableName)

    alterTable(cursor, tableName)

    for information in informations:
      peer = information['description']['peer']
      description = information['description']['content']
      asNumber = information['as-number']['content']
      connectInterface = information['connect-interface']['content']
      ip = gadget['ip']
      gadgetName = gadget['equipamento']

      registry = getRegistry(cursor, tableName, ip, peer)

      if registry != None:
        registryAsNumber = registry[4]
        registryDescription = registry[5]
        registryConnectInterface = registry[6]

        if (asNumber != registryAsNumber or description != registryDescription or connectInterface != registryConnectInterface):
          updateItem = f"""UPDATE {tableName}
                        SET as_number='{registryAsNumber}',
                        description='{registryDescription}'
                        connect_interface='{registryConnectInterface}'
                        WHERE ip='{ip}' and peer='{peer}';
                      """
          cursor.execute(updateItem)

        continue

      createRegistry(conn, cursor, tableName, gadgetName, ip, peer, asNumber, description, connectInterface)

    print('dados atualizados')  
    
    cursor.close()
    conn.close()  

runCommands()
