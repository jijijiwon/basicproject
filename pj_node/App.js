const express = require("express");
const morgan = require("morgan");
const path = require("path");
const app = express();
const bodyParser = require("body-parser");

app.set("port", process.env.PORT || 8000);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, "public")));

var main = require("./routes/Main.js");
app.use("/", main);

app.listen(app.get("port"), () => {
  console.log("8000 Port : Server Started~!!");
});
