require('dotenv').config()

const express = require('express')
const axios = require('axios')
const qrcode = require('qrcode-terminal')

const {
  Client,
  LocalAuth
} = require('whatsapp-web.js')

const app = express()

app.use(express.json())

// ====================================
// CONFIG
// ====================================

const PORT =
  process.env.PORT || 3000

const API_URL =
  process.env.API_URL

// ====================================
// STORAGE
// ====================================

const sessions = {}

const qrCodes = {}

const connectedSessions = {}

// ====================================
// CREATE SESSION
// ====================================

function createSession(assistantId) {

  if (sessions[assistantId]) {

    return sessions[assistantId]

  }

  const client = new Client({

    authStrategy: new LocalAuth({

      clientId: assistantId

    }),

    puppeteer: {

      headless: true,

      args: [

        '--no-sandbox',

        '--disable-setuid-sandbox',

        '--disable-dev-shm-usage',

        '--disable-accelerated-2d-canvas',

        '--disable-gpu'

      ]

    }

  })

  // ====================================
  // QR
  // ====================================

  client.on('qr', (qr) => {

    qrCodes[assistantId] = qr

    connectedSessions[assistantId] = false

    console.log('\n====================')
    console.log('QR GENERATED')
    console.log('====================\n')

    qrcode.generate(qr, {
      small: true
    })

  })

  // ====================================
  // READY
  // ====================================

  client.on('ready', () => {

    connectedSessions[assistantId] = true

    console.log('\n====================')
    console.log(`CONNECTED : ${assistantId}`)
    console.log('====================\n')

  })

  // ====================================
  // AUTH FAILURE
  // ====================================

  client.on('auth_failure', (msg) => {

    console.log('\n====================')
    console.log('AUTH FAILURE')
    console.log('====================\n')

    console.log(msg)

  })

  // ====================================
  // DISCONNECTED
  // ====================================

  client.on('disconnected', (reason) => {

    connectedSessions[assistantId] = false

    console.log('\n====================')
    console.log('DISCONNECTED')
    console.log('====================\n')

    console.log(reason)

  })

  // ====================================
  // MESSAGE
  // ====================================

  client.on('message', async (message) => {

    try {

      if (message.fromMe) {
        return
      }

      if (message.from.includes('@g.us')) {
        return
      }

      if (message.from === 'status@broadcast') {
        return
      }

      if (message.broadcast) {
        return
      }

      if (!message.body) {
        return
      }

      console.log('\n====================')
      console.log('NEW MESSAGE')
      console.log('====================\n')

      console.log(message.body)

      const response =
        await axios.post(

          `${API_URL}/ai-response`,

          {

            assistant_id:
              assistantId,

            phone:
              message.from,

            message:
              message.body

          }

        )

      console.log('\n====================')
      console.log('AI RESPONSE')
      console.log('====================\n')

      console.log(response.data)

      if (

        !response.data.assistant_status

      ) {

        return

      }

      await client.sendMessage(

        message.from,

        response.data.reply

      )

    } catch (error) {

      console.log('\n====================')
      console.log('ERROR')
      console.log('====================\n')

      console.log(

        error.response?.data ||

        error.message

      )

    }

  })

  // ====================================
  // INITIALIZE
  // ====================================

  client.initialize()

  sessions[assistantId] = client

  return client

}

// ====================================
// HOME
// ====================================

app.get('/', (req, res) => {

  res.json({

    status:
      'ChatGLN WhatsApp Engine Online 🚀'

  })

})

// ====================================
// START
// ====================================

app.get('/start/:assistantId', (req, res) => {

  const assistantId =
    req.params.assistantId

  createSession(assistantId)

  res.json({

    success: true,

    qr_page:

      `${req.protocol}://${req.get('host')}/qr/${assistantId}`

  })

})

// ====================================
// QR PAGE
// ====================================

app.get('/qr/:assistantId', (req, res) => {

  const assistantId =
    req.params.assistantId

  res.send(`

<!DOCTYPE html>

<html>

<head>

<title>

ChatGLN QR

</title>

<meta charset="UTF-8" />

<meta
  name="viewport"
  content="width=device-width, initial-scale=1.0"
/>

<style>

* {

  margin: 0;

  padding: 0;

  box-sizing: border-box;

}

body {

  background: #000000;

  color: #ffffff;

  font-family: Arial, sans-serif;

  display: flex;

  justify-content: center;

  align-items: center;

  min-height: 100vh;

  padding: 20px;

}

.container {

  width: 100%;

  max-width: 400px;

  text-align: center;

}

.card {

  border: 1px solid #ffffff22;

  border-radius: 24px;

  padding: 35px 25px;

  background: #111111;

}

.logo {

  font-size: 38px;

  font-weight: bold;

  margin-bottom: 15px;

  letter-spacing: 2px;

}

.subtitle {

  color: #aaaaaa;

  margin-bottom: 30px;

  font-size: 15px;

}

.qr-box {

  background: white;

  padding: 12px;

  border-radius: 20px;

  display: inline-block;

}

.qr-box img {

  width: 280px;

  height: 280px;

  display: block;

}

button {

  margin-top: 25px;

  width: 100%;

  border: none;

  background: #ffffff;

  color: #000000;

  padding: 16px;

  border-radius: 14px;

  font-size: 16px;

  font-weight: bold;

  cursor: pointer;

}

.loader {

  width: 55px;

  height: 55px;

  border: 3px solid #222222;

  border-top: 3px solid white;

  border-radius: 50%;

  margin: auto;

  animation: spin 1s linear infinite;

}

@keyframes spin {

  100% {

    transform: rotate(360deg);

  }

}

</style>

</head>

<body>

<div class="container">

<div class="card">

<div id="content">

<div class="logo">

ChatGLN

</div>

<div class="subtitle">

Génération du QR Code...

</div>

<div class="loader"></div>

</div>

</div>

</div>

<script>

async function loadQR() {

  const response = await fetch(

    '/qr-data/${assistantId}'

  )

  const data = await response.json()

  if (data.connected) {

    document.getElementById(

      'content'

    ).innerHTML = \`

      <div class="logo">

        ChatGLN

      </div>

      <h1>

        Connecté ✅

      </h1>

    \`

    return

  }

  if (!data.qr) {

    return

  }

  const qrImage =

    'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=' +

    encodeURIComponent(data.qr)

  document.getElementById(

    'content'

  ).innerHTML = \`

    <div class="logo">

      ChatGLN

    </div>

    <div class="subtitle">

      Scanner avec WhatsApp

    </div>

    <div class="qr-box">

      <img src="\${qrImage}" />

    </div>

    <a href="\${qrImage}" download>

      <button>

        Télécharger QR

      </button>

    </a>

  \`

}

loadQR()

setInterval(loadQR, 3000)

</script>

</body>

</html>

  `)

})

// ====================================
// QR DATA
// ====================================

app.get('/qr-data/:assistantId', (req, res) => {

  const assistantId =
    req.params.assistantId

  res.json({

    connected:

      connectedSessions[
        assistantId
      ] || false,

    qr:

      qrCodes[
        assistantId
      ] || null

  })

})

// ====================================
// SERVER
// ====================================

app.listen(PORT, () => {

  console.log('\n====================')
  console.log(`SERVER RUNNING : ${PORT}`)
  console.log('====================\n')

})
