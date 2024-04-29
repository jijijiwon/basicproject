const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");
const XMLHttpRequest = require("xhr2");
const app = express();

app.get("/Hello", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000");
  res.json(resp.data);
});

app.get("/users", async (req, res) => {
  const resp = await axios.get("http://192.168.1.64:3000/users-list");
  res.json(resp.data);
});

app.get("/search", (req, res) => {
  const xhr = new XMLHttpRequest();
  const { Sx, Sy, Ex, Ey } = req.query; // 요청 파라미터에서 Sx, Sy, Ex, Ey 값을 가져옴

  // 요청 파라미터로부터 URL 생성
  const url = `http://192.168.1.64:3000/searchSubway?Sx=${Sx}&Sy=${Sy}&Ex=${Ex}&Ey=${Ey}`;

  // 생성된 URL을 로그로 출력
  console.log("Generated URL:", url);

  xhr.open("GET", url);
  xhr.setRequestHeader("content-type", "application/json");
  xhr.send();

  xhr.onload = () => {
    if (xhr.status === 200) {
      const res = JSON.parse(xhr.response);
      console.log(res);
    } else {
      console.log(xhr.status, xhr.statusText);
    }
    res.send(xhr.response);
  };
});

// app.get("/search", async () => {
//   const searchSubway = async (Sx, Sy, Ex, Ey) => {
//     try {
//       // FastAPI 서버의 URL
//       const apiUrl = "http://192.168.1.71:3000/searchSubway";

//       // 요청 데이터
//       const requestData = {
//         Sx: Sx,
//         Sy: Sy,
//         Ex: Ex,
//         Ey: Ey,
//       };

//       // FastAPI 서버에 POST 요청 보내기
//       const response = await axios.get(apiUrl, { params: requestData });

//       // 응답 데이터 확인
//       console.log("Response:", response.data);

//       // 여기에서 응답 데이터를 처리하거나 반환할 수 있습니다.
//       return response.data;
//     } catch (error) {
//       // 오류 처리
//       console.error("Error:", error.response.data);
//       throw error;
//     }
//   };
// });
// // // 테스트를 위한 호출
// // const Sx = 37.12345;
// // const Sy = 127.54321;
// // const Ex = 37.98765;
// // const Ey = 126.98765;

// // searchSubway(Sx, Sy, Ex, Ey);

module.exports = app;
