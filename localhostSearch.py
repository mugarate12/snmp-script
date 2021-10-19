import os
import mysql.connector
from mysql.connector import errorcode

# database informations
database_host = 'localhost'
database_user= 'root'
database_password= ''

community = 'W1r3l1nk'
ip = '172.31.3.106'
oids = 'iso.3.6.1.4.1.2011.5.25.191.2.1.1.8'

gadgets = [
  {
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
  searchResult = os.popen(filter).read().split('\n')

  return searchResult

def searchWithPeer(peer, arraySearch):
  for search in arraySearch:
    if peer in search:
      return search

def informationPerPeer(descriptionArraySearch, asNumberArraySearch, connectInterfaceArraySearch):
  informations = []

  for descriptionSearch in descriptionArraySearch:
    if len(descriptionSearch) > 0:
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
    conn = mysql.connector.connect(
      user=database_user,
      password=database_password,
      host=database_host
    )

    try:
      conn
      print('connection with database ok')
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACESS_DANIED_ERROR:
        print('user or password of database wrong')
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print('database not exists')
      else:
        print(err)
    else:
        cursor = conn.cursor()
      
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")
    cursor.execute(f"use {databaseName}")

    createTable = f"""CREATE TABLE IF NOT EXISTS {tableName} 
                    (id                 int not null auto_increment primary key,
                    equipamento         int,
                    ip                  varchar(200),
                    peer                varchar(200),
                    as_number           varchar(200),
                    description         varchar(200),
                    connect_interface   varchar(200));
             """
    cursor.execute(createTable)

    for information in informations:
      peer = information['description']['peer']
      description = information['description']['content']
      asNumber = information['as-number']['content']
      connectInterface = information['connect-interface']['content']
      ip = gadget['ip']

      getLastItemQuery = f"""SELECT equipamento, ip from {tableName}
                            ORDER BY id DESC LIMIT 1;
                        """
      cursor.execute(getLastItemQuery)
      lastItem = cursor.fetchone()
      lastGadgetIndex = int(1)

      getGadgetIndexIfGadgetIpExists = f""" SELECT equipamento from {tableName}
                                  WHERE ip='{ip}'
                                  LIMIT 0, 1;
                            """
      cursor.execute(getGadgetIndexIfGadgetIpExists)
      ipOfGadgetInDatabase = cursor.fetchone()

      if lastItem != None:
        if ipOfGadgetInDatabase != None:
          lastGadgetIndex = int(ipOfGadgetInDatabase[0])
        else:
          lastGadgetIndex = int(lastItem[0]) + 1

      verifyExistsRegistry = f""" SELECT * from {tableName}
                                  WHERE ip='{ip}' and peer='{peer}';
                            """
      cursor.execute(verifyExistsRegistry)
      registry = cursor.fetchone()

      print(f'lastGadgetIndex: {lastGadgetIndex}')

      if registry != None:
        continue

      createItem = f"""INSERT INTO {tableName}
                      (equipamento, ip, peer, as_number, description, connect_interface) 
                    VALUES
                      ({lastGadgetIndex}, "{ip}", "{peer}", "{asNumber}", "{description}", "{connectInterface}");
                  """
      cursor.execute(createItem)
      conn.commit()
    
    cursor.close()
    conn.close()  

runCommands()
