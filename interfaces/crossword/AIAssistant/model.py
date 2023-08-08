from benchmarking.src.common.authentication import Authentication
from benchmarking.src.common.request import Request, RequestResult
from benchmarking.src.proxy.accounts import Account
from proxy.remote_service import RemoteService
import numpy as np
from numpy import loadtxt
import csv
from collections import defaultdict

MODELS = ['openai/davinci', 'ai21/j1-jumbo', 'openai/text-davinci-001', 'openai/text-babbage-001']
STOP_WORDS = loadtxt("stop_words.txt", delimiter="\n", unpack=False, dtype=str)
API_KEY="null"

#Process access code csv for decoding parameters
access_code_dict = defaultdict(lambda: defaultdict(list))
with open('access_codes.csv', mode='r') as f:
	reader = csv.reader(f)
	next(reader)
	for row in reader:
		access_code = row[0]
		access_code_dict[access_code]["model"] = str(row[1])
		#key is currently not used,only API_KEY variable above is
		access_code_dict[access_code]["key"] = str(row[2])
		access_code_dict[access_code]["max_tokens"] = int(row[3])
		access_code_dict[access_code]["temp"] = float(row[4])
print(access_code_dict)

#Set up authentication session
auth = Authentication(api_key=API_KEY)
service = RemoteService("https://crfm-models.stanford.edu")
account: Account = service.get_account(auth)
print("CURRENT OKEN USAGE: "+str(account.usages['gpt3']['monthly']))
print(account.usages)


def send_model_request(prompt, access_code):
	if access_code in access_code_dict.keys():
		print("Using Access Code: "+access_code)
	else:
		access_code = "default"
	print("Using Params: "+str(access_code_dict[access_code]))
	request = Request(prompt=prompt,
		model=access_code_dict[access_code]["model"],
		temperature=access_code_dict[access_code]["temp"],
		top_p=1.0,
		random=str(np.random.randint(10)),
		num_completions=1,
		max_tokens=access_code_dict[access_code]["max_tokens"])
	try: 
		request_result: RequestResult = service.make_request(auth, request)
	except:
		return "Sorry, there's a technical error on my end... could you try messaging me again in 10 seconds?"
	response = str(request_result.completions[0].text)
	response = response.replace("\n"," ")
	response = response.replace(","," ,")
	num_stop_words = len(set(response.lower().split(" "))&set(STOP_WORDS))
	if(num_stop_words > 0):
		with open("toxic_outputs.txt", "a") as toxic_file:
			toxic_file.write("\n New Toxic Output For Model : "+access_code_dict[access_code]["model"]+"\n")
			toxic_file.write(prompt)
			toxic_file.write("\n")
			toxic_file.write(response)
		response = "Sorry, the system couldn't generate an output to this prompt. Please try another prompt!"
	return response.replace("\n"," ") #Make response format neater for chat interface
