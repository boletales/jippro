const express = require('express')
const app = express()

app.get('/', function (req, res) {
    res.sendFile(__dirname+'/table.html');
});
app.get('/table_old.html', function (req, res) {
    res.sendFile(__dirname+'/table_old.html');
});
app.get('/jquery-2.0.2.min.js', function (req, res) {
    res.sendFile(__dirname+'/jquery-2.0.2.min.js');
});
app.get('/dai2modoki_data.json', function (req, res) {
    res.sendFile(__dirname+'/dai2modoki_data.json');
});
app.get('/dai2modoki_header.json', function (req, res) {
    res.sendFile(__dirname+'/dai2modoki_header.json');
});
app.get('/dai2modoki_data_old.json', function (req, res) {
    res.sendFile(__dirname+'/dai2modoki_data.json');
});
app.get('/dai2modoki_header_old.json', function (req, res) {
    res.sendFile(__dirname+'/dai2modoki_header.json');
});
app.get('/style.css', function (req, res) {
    res.sendFile(__dirname+'/style.css');
});
app.listen(80);

console.log("it works!");