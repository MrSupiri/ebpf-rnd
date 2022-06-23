const axios = require('axios');
const express = require('express')
const app = express()

app.get('/http', function (req, res) {
    axios.get('http://postman-echo.com/get?foo1=bar1&foo2=bar2')
    .then(res => {
        console.log(res.data);
    })
    .catch(error => {
        console.error(error);
    })
    .finally(() => {
        res.sendStatus(200);
      });
    ;
})

app.get('/https', function (req, res) {
    axios.get('https://postman-echo.com/get?foo1=bar1&foo2=bar2')
    .then(res => {
        console.log(res.data);
    })
    .catch(error => {
        console.error(error);
    })
    .finally(() => {
        res.sendStatus(200);
      });
    ;
})

app.get('/empty', function (req, res) {
    res.sendStatus(200);
})


app.listen(9093)