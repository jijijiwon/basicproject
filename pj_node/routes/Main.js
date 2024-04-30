const express = require("express");
const axios = require("axios");
const async = require("async");
const querystring = require("querystring");
const bodyParser = require("body-parser");
const app = express();

app.get("/Hello", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000");
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

app.get("/search", async (req, res) => {
  const { Sx, Sy, Ex, Ey } = req.query;

  try {
    const responseS1 = await query1(Sx, Sy, Ex, Ey);
    console.log("ResponseS1:", responseS1);

    const responseS2 = await query2(responseS1);
    console.log("ResponseS2:", responseS2);

    const responseB1 = await query3(Sx, Sy, Ex, Ey);
    console.log("ResponseB1:", responseB1);

    const responseB2 = await query4(responseB1);
    console.log("ResponseB2:", responseB2);

    const responseB3 = await query5(responseB2);
    console.log("ResponseB3:", responseB3);

    const responseB4 = await query6(responseB3);
    console.log("ResponseB4:", responseB4);

    const resCompare = { SId: responseS2.SId, BId: responseB4.BId };
    const responseFinal = await query7(resCompare);
    console.log("responseFinal:", responseFinal);

    res.send(responseFinal); // 마지막 결과 전송
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Internal Server Error");
  }
});

function query1(Sx, Sy, Ex, Ey) {
  return sendRequest("GET", "http://192.168.1.64:3000/searchSubway", {
    Sx: Sx,
    Sy: Sy,
    Ex: Ex,
    Ey: Ey,
  });
}

function query2(response1) {
  return sendRequest(
    "POST",
    "http://192.168.1.64:3000/saveSubwayPath",
    {},
    { coordinates: response1.coordinates, TempId: response1.TempId }
  );
}

function query3(Sx, Sy, Ex, Ey) {
  return sendRequest("GET", "http://192.168.1.64:3000/searchBus", {
    Sx: Sx,
    Sy: Sy,
    Ex: Ex,
    Ey: Ey,
  });
}

function query4(response1) {
  return sendRequest(
    "POST",
    "http://192.168.1.64:3000/saveBusPath",
    {},
    { coordinates: response1.coordinates, TempId: response1.TempId }
  );
}

function query5(response2) {
  return sendRequest(
    "PATCH",
    "http://192.168.1.64:3000/bikeStation",
    {},
    { BId: response2.BId }
  );
}

function query6(response3) {
  return sendRequest(
    "PATCH",
    "http://192.168.1.64:3000/updateBusPath",
    {},
    { BId: response3.BId }
  );
}

function query7(resCompare) {
  return sendRequest(
    "POST",
    "http://192.168.1.64:3000/saveSql",
    {},
    { SId: resCompare.SId, BId: resCompare.BId }
  );
}

module.exports = app;
