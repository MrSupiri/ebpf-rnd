import cProfile
import requests

def foo():
    r = requests.get("https://postman-echo.com/get?foo1=bar1&foo2=bar2")
    

cProfile.run('foo()')