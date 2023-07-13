from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
import model
import urllib.parse
import json
import os
import pickle
import atexit
import logging
from datetime import datetime

simulation_mode = False

app = Flask(__name__)


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

api_server_state = dict()
api_server_state_filename = "api_server_state.pickle"

logdirname = "logs"
logfile_handles = dict()

@atexit.register
def dump_api_server_state():
  try:
    with open(api_server_state_filename, 'wb') as handle:
      pickle.dump(api_server_state, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Successfully save state to {api_server_state_filename}")
  except Exception as error:
    print(f"Could not save state to {api_server_state_filename}: {error}")

def load_api_server_state():
  try:
    with open(api_server_state_filename, 'rb') as handle:
      api_server_state = pickle.load(handle)
    print(f"Successfully loaded state from {api_server_state_filename}")
    for k in api_server_state:
      print(f"\t{k}:   {api_server_state[k]}")
  except Exception as error:
    print(f"Could not load state from {api_server_state_filename}: {error}")

def disable_gpt3_access(pid,uid):
  key = (pid,uid)
  if key not in api_server_state:
    api_server_state[key] = dict()
  api_server_state[key]["gpt3_access"] = False

def enable_gpt3_access(pid,uid):
  key = (pid,uid)
  if key not in api_server_state:
    api_server_state[key] = dict()
  api_server_state[key]["gpt3_access"] = True
  api_server_state[key]["first_gpt3_access_ts"] = datetime.timestamp(datetime.now())
  print(f"GPT3 access enabled for {pid}_{uid}")

def check_gpt3_access(pid,uid):
  if(uid=="1509679a"): #Special permissions for Debug's laptop :) 
    return True
  key = (pid,uid)
  if key not in api_server_state or "gpt3_access" not in api_server_state[key]:
    enable_gpt3_access(pid,uid)
    return True
  elif not api_server_state[key]["gpt3_access"]:
    return False
  else:
    ts = datetime.timestamp(datetime.now())
    if (ts-api_server_state[key]["first_gpt3_access_ts"])>(2*60*60):
      # two hours have elapsed since first access - disable further GPT-3 access
      api_server_state[key]["gpt3_access"] = False
    return api_server_state[key]["gpt3_access"]

def log_to_file(pid,uid,username, message,endchar="\n"):
  logfilename = f"{logdirname}/{pid}_{uid}_{username}"
  key = (pid,uid)
  if key not in logfile_handles:
    try:
      logfile = open(logfilename,'a+')
      logfile.write(message+endchar)
    except Exception as error:
      print(f"Could not log message to {logfilename}: {error}")
  elif logfile_handles[key]:
    logfile_handles[key].write(message+endchar)
  else:
    try:
      logfile = open(logfilename,'a+')
      logfile.write(message+endchar)
      logfile.close()
    except Exception as error:
      print(f"Could not log message to {logfilename}: {error}")

def close_logfile(pid,uid):
  try:
    key = (pid,uid)
    if key in logfile_handles and logfile_handles[key]:
      logfile_handles[key].close()
  except:
    pass
  logfile_handles[key] = None

@app.route("/ask")
def home():
  uid = request.args.get('uid')
  pid = request.args.get('pid')
  query = request.args.get('query')
  url = urllib.parse.unquote(request.args.get('url'))
  gid = url.rsplit('/',1)[1]
  api_server_state[gid] = pid
  parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
  access_code = "default"
  username = "default"
  if 'code' in parsed_url.keys():
    access_code =  parsed_url['code'][0]
  if 'username' in parsed_url.keys():
    username =  parsed_url['username'][0]
  timestamp = request.args.get('timestamp')
  query_csv = query.replace('"','""')
  log_message = f'Ask, {timestamp}, {pid}, {uid}, "{query_csv}"'
  log_to_file(pid,uid,username,log_message)
  if not check_gpt3_access(pid,uid):
    response = make_response("Sorry, but you are no longer allowed access to the AI.")
  elif query==None:
    response = make_response("Hi!")
  elif simulation_mode:
    response = make_response(f"Sorry, I can't answer '{query}'")
  else:
    model_response = model.send_model_request(query, access_code)
    model_response_csv = model_response.replace('"','""')
    model_response_message = f'Model Answer, {timestamp}, {pid}, {uid}, "{model_response_csv}"'
    log_to_file(pid,uid,username,model_response_message)
    response = make_response(f""+model_response) 
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response

@app.route("/log")
def log():
  message = urllib.parse.unquote(request.args.get('message'))
  message_split = message.split(',')
  message_type = message_split[0]
  #print("\n*** "+message)
  #print(message_type)
  if message_type=='GameInFocus':
    # GameInFocus,id,pid,timestamp,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    url = message_split[4]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[5:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"GameInFocus, {timestamp}, {pid}, {uid}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  elif message_type=='GameBlurred':
    # GameBlurred,id,pid,timestamp,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    url = message_split[4] 
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[5:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"GameBlurred, {timestamp}, {pid}, {uid}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  elif message_type=='CellUpdate':
    # CellUpdate,id,pid,timestamp,r,c,value,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    row = message_split[4]
    col = message_split[5]
    val = message_split[6]
    url = message_split[7]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[8:]))  
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"CellUpdate, {timestamp}, {pid}, {uid}, {row}, {col}, {val}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
    """
    other options:
    print(cwstate['grid'])
    print(cwstate['solution'])
    print(cwstate['circles'])
    print(cwstate['chat'])
    print(cwstate['clues'])
    print(cwstate['solved'])
    print(cwstate['clock'])
    print(cwstate['cursors'])
    print(cwstate['users'])
    print(cwstate['themeColor'])
    print(cwstate['optimisticCounter'])
    """
  elif message_type=='ResetClock':
    # ResetClock,id,pid,timestamp,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    url = message_split[4]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[5:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"ResetClock, {timestamp}, {pid}, {uid}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  elif message_type=='Check':
    # Check,id,pid,timestamp,scopeString,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    scopeString = message_split[4]
    url = message_split[5]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[6:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"Check, {timestamp}, {pid}, {uid}, {scopeString}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  elif message_type=='Reveal':
    # Reveal,id,pid,timestamp,scopeString,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    scopeString = message_split[4]
    url = message_split[5]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[6:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"Reveal, {timestamp}, {pid}, {uid}, {scopeString}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  elif message_type=='Reset':
    # Reset,id,pid,timestamp,scopeString,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    scopeString = message_split[4]
    url = message_split[5]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[6:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"Reset, {timestamp}, {pid}, {uid}, {scopeString}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  elif message_type=='GiveUp':
    # GiveUp,id,pid,timestamp,secretCode,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    secretCode = message_split[4]
    url = message_split[5]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[6:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"GiveUp, {timestamp}, {pid}, {uid}, {secretCode}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
    disable_gpt3_access(pid,uid)
    close_logfile(pid,uid)
  elif message_type=='Solved':
    # Solved,id,pid,timestamp,secretCode,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    secretCode = message_split[4]
    url = message_split[5]
    gid = url.rsplit('/',1)[1]
    api_server_state[gid] = pid
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[6:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"Solved, {timestamp}, {pid}, {uid}, {secretCode}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
    disable_gpt3_access(pid,uid)
    close_logfile(pid,uid)
  elif message_type=='NewClueSelected':
    # NewClueSelected,id,-1,timestamp,number,direction,url,gameState
    uid = message_split[1]
    pid = message_split[2]
    timestamp = message_split[3]
    number = message_split[4]
    direction = message_split[5]
    url = message_split[6]
    gid = url.rsplit('/',1)[1]
    if pid=="null" and gid in api_server_state:
      pid = api_server_state[gid]
    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    access_code = "default"
    username = "default"
    if 'code' in parsed_url.keys():
      access_code =  parsed_url['code'][0]
    if 'username' in parsed_url.keys():
      username =  parsed_url['username'][0]
    cwstate = json.loads(','.join(message_split[7:]))
    if pid not in api_server_state:
      api_server_state[pid] = {"clues": cwstate["clues"], "solution": cwstate["solution"]}
    grid_state = [[c['value'] for c in r] for r in cwstate['grid']]
    log_message = f"NewClueSelected, {timestamp}, {pid}, {uid}, {number}, {direction}, {url}, {access_code}, {username}, \"{grid_state}\""
    print(log_message)
    log_to_file(pid,uid,username,log_message)
  else:
    # unknown
    message_csv = message.replace('"','""')
    log_message = f'Unknown, , , , "{message_csv}"'
    print(log_message)
  response = make_response(f"")
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response
  
if __name__ == "__main__":
  load_api_server_state()
  log_subdir = logdirname
  if not os.path.exists(log_subdir): os.makedirs(log_subdir)
  app.run(host="0.0.0.0")