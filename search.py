# from paramiko import SSHClient
import paramiko

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

command = f'snmpwalk -v2c -c {community} {ip} {oids} | grep peer'
filterByDescription = f'{command} | grep description'

stdin, stdout, stderr = ssh.exec_command(command)
searchResult = stdout.readlines()

print(searchResult[0])
print(searchResult[1])
print(searchResult[2])

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

  print(f'{filterString}\nid: {searchID}\npeer: {peer}\ncontent: {content}\n')

print(f'ip:\n{ip}\n')

asNumber = searchResult[0]
getInformations(asNumber, 'as-number')

description = searchResult[1]
getInformations(description, 'description')

connectInterface = searchResult[2]
getInformations(connectInterface, 'connect-interface')
