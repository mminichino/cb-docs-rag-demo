# Couchbase Vector Demo 1.0.0

## Prerequisites
- OpenAI API key

Steps to set up and run the demo:
```
python3 -m venv docs_demo
```
```
. rag_demo/bin/activate
```
```
pip install git+https://github.com/mminichino/cb-docs-rag-demo
```
```
curl -OLs https://github.com/mminichino/cb-docs-rag-demo/releases/download/1.0.0/docdemo-1.0.0.gz
```
```
demo_prep -h cbnode-0001.example.com -u Administrator -p 'password'
```
```
data_load -h cbnode-0001.example.com -u Administrator -p 'password' -f docdemo-1.0.0.gz
```
```
demo_run
```
To exit from the Python virtual environment:
```
deactivate
```
- You can also pass parameters to ```demo_run``` and they will be populated in the UI.
- If the environment variable OPENAI_API_KEY is set, it will be imported into the UI.

| Option                 | Description                 |
|------------------------|-----------------------------|
| -u                     | User Name                   |
| -p                     | User Password               |
| -h                     | Cluster Node or Domain Name |
| -b                     | Bucket name                 |
| -s                     | Scope name                  |
| -c                     | Collection name             |
| -i                     | Index name                  |
| -K                     | OpenAI API Key              |
