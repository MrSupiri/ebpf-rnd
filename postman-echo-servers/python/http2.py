import json
from flask import Flask
import os
import httpx

app = Flask(__name__)
print("PID:", os.getpid())

@app.route('/http')
async def http():
    client = httpx.AsyncClient(http2=True)
    r = await client.get("http://postman-echo.com/get?foo1=bar1&foo2=bar2")
    print(r.http_version)  # "HTTP/1.0", "HTTP/1.1", or "HTTP/2".
    print("Resp:", r.json())
    return ('', 200) 

@app.route('/https')
async def https():
    client = httpx.AsyncClient(http2=True)
    r = await client.get("https://postman-echo.com/get?foo1=bar1&foo2=bar2")
    print(r.http_version)  # "HTTP/1.0", "HTTP/1.1", or "HTTP/2".
    print("Resp:", r.json())
    return ('', 200) 

@app.route('/https/large')
async def http_large():
    file = open('../data.blob', 'rb').read()
    client = httpx.AsyncClient(http2=False)
    r = await client.put("https://postman-echo.com/put/data.blob", data=file)
    print(r.http_version)  # "HTTP/1.0", "HTTP/1.1", or "HTTP/2".
    # print("Resp:", r.statu)
    return ('', 200) 


@app.route('/empty')
def empty():
    return ('', 200) 


app.run(port=9094)