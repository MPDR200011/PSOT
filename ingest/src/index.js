import express from 'express';

const app = express();
const port = 8081;

app.use(express.json())

app.post('/ingest', (req, res) => {
    console.log(`received stuff: ${JSON.stringify(req.body)}`)
    res.send('OK')
})

app.listen(port, () => {
    console.log(`Ingest listenning at port: ${port}`)
})
