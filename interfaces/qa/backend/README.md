# How to set up your API key(s)

1. Create `api_key.csv` with host name(s), domain name(s), and API key(s).

```
host    domain          api_key                                   
openai  default         sk-***************************************
crfm    default         ***************************                
crfm    interaction     **************************                           
```

Note that you need to set at least one default API key for either `openai` or `crfm`.

2. Run `api_server.py` by providing a path to `api_key.csv`.

`./run.sh`
