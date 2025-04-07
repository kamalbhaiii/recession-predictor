const express = require('express');
const { PythonShell } = require('python-shell');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv')
const path = require('path')

dotenv.config()

const app = express();
app.use(cors());
app.use(express.json());

mongoose.connect(process.env.EXPRESS_MONGO, { useNewUrlParser: true });

const DataSchema = new mongoose.Schema({ date: String, features: Object, prediction: Number });
const Data = mongoose.model('Data', DataSchema);

// SSE Clients
let clients = [];

app.get('/logs', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Add client to list
    clients.push(res);

    // Remove client when they disconnect
    req.on('close', () => {
        clients = clients.filter(client => client !== res);
    });
});

function sendLogToClients(log) {
    clients.forEach(client => {
        client.write(`data: ${log}\n\n`);
    });
}

app.get('/test', (req,res)=>{
    res.status(200).send({
        message:"Server is live."
    })
})

app.get('/fetch', async (req,res) => {
    const stats = await Data.find()

    res.status(200).send(stats)  
})

app.post('/predict', (req, res) => {
    let options = {
        mode: 'text',
        pythonPath: `${process.env.EXPRESS_PYTHON_PATH}`,
        scriptPath: path.join(__dirname, '../python'),
        args: [JSON.stringify(req.body.features)]
    };

    sendLogToClients("🔄 Starting Python script...");

    let pyshell = new PythonShell('predict.py', options);

    let prediction;

    pyshell.on('message', (message) => {
        if (message.includes('Prediction result:')) {
            prediction = message.split(':')[1]
        }
        sendLogToClients(`📜 Python: ${message}`);
    });

    pyshell.on('stderr', (err) => {
        sendLogToClients(`❌ Error: ${err}`);
    });

    pyshell.end((err, code, signal) => {
        if (err) {
            console.log(err)
            sendLogToClients("❌ Python script error. Check the logs.");
            return res.status(500).send("Python script error.");
        }
        sendLogToClients("✅ Prediction complete.");
        const newData = new Data({ date: new Date(), features: req.body.features, prediction });
        newData.save();
        res.json({ prediction:parseFloat(prediction) });
    });
});

app.listen(process.env.EXPRESS_PORT, () => console.log(`Server running on port ${process.env.EXPRESS_PORT}`));
