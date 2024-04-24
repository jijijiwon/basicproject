const express = require("express");
const axios = require("axios");
const app = express.Router();

app.get("/Hello", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000");
  res.json(resp.data);
});

app.get("/users", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000/users-list");
  res.json(resp.data);
});

module.exports = app;
