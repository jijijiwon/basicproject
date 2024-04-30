const express = require("express");
const axios = require("axios");
const querystring = require("querystring");
const bodyParser = require("body-parser");
const app = express();

app.get("/Hello", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000");
  res.json(resp.data);
});

app.get("/users", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000/users-list");
  res.json(resp.data);
});

async function sendRequest(method, url, queryParams = {}, body = {}) {
  try {
    const queryString = querystring.stringify(queryParams);
    const config = {
      method: method.toUpperCase(),
      url: queryString ? `${url}?${queryString}` : url,
      headers: {
        "Content-Type": "application/json",
      },
      data: body,
    };

    const response = await axios(config);
    return response.data;
  } catch (error) {
    throw error;
  }
}

app.get("/searchSubway", (req, res) => {
  const { Sx, Sy, Ex, Ey } = req.query;
  sendRequest("GET", "http://192.168.1.64:3000/searchSubway", {
    Sx: Sx,
    Sy: Sy,
    Ex: Ex,
    Ey: Ey,
  }).then((response1) => {
    console.log("Response:", response1);
    sendRequest(
      "POST",
      "http://192.168.1.64:3000/saveSubwayPath",
      {},
      { coordinates: response1.coordinates, TempId: response1.TempId }
    )
      .then((response2) => {
        console.log("Response:", response2);
        res.send(response2);
      })
      .catch((error) => {
        console.error("Error:", error);
        res.status(500).send("Internal Server Error");
      });
  });
});

app.get("/searchBusBike", (req, res) => {
  const { Sx, Sy, Ex, Ey } = req.query;
  sendRequest("GET", "http://192.168.1.64:3000/searchBus", {
    Sx: Sx,
    Sy: Sy,
    Ex: Ex,
    Ey: Ey,
  }).then((response1) => {
    console.log("Response1:", response1);
    sendRequest(
      "POST",
      "http://192.168.1.64:3000/saveBusPath",
      {},
      { coordinates: response1.coordinates, TempId: response1.TempId }
    ).then((response2) => {
      console.log("Response2:", response2);
      sendRequest(
        "PATCH",
        "http://192.168.1.64:3000/bikeStation",
        {},
        { BId: response2.BId }
      )
        .then((response3) => {
          console.log("Response3:", response3);
          // console.log(typeof response3);
          // res.send(response3);
          sendRequest(
            "PATCH",
            "http://192.168.1.64:3000/updateBusPath",
            {},
            { BId: response3.BId }
          ).then((response4) => {
            console.log("Response4:", response4);
            res.send(response4);
          });
        })

        .catch((error) => {
          console.error("Error:", error);
          res.status(500).send("Internal Server Error");
        });
    });
  });
});

module.exports = app;
