import pickle


api_server_state = dict()
api_server_state_filename = "api_server_state.pickle"


def load_api_server_state():
  try:
    with open(api_server_state_filename, 'rb') as handle:
      api_server_state = pickle.load(handle)
    print(f"Successfully loaded state from {api_server_state_filename}")
    for k in api_server_state:
      print(f"\t{k}:   {api_server_state[k]}")
  except Exception as error:
    print(f"Could not load state from {api_server_state_filename}: {error}")

if __name__ == "__main__":
  load_api_server_state()