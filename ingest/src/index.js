import express from 'express';
const { Pool } = require('pg')
let format = require('pg-format');

const pool = new Pool({
    user: 'jeronimo',
    host: 'psot_db',
    database: 'psot_info',
    password: 'password123',
    port: 5432,
})

const app = express();
const port = 8081;

app.use(express.json())
/*{
    "scanTime": 0,
    "place": <placeid>,
    "wifiAccessPoints": [
        {
            "name": "",
            "macAddress": "",
            "numConnectedClients": 0,
            "concreteDetectedClients": [
                {
                    "macAddress": ""
                },
                .
                .
                .
            ]
        },
        .
        .
        .
    ]
}*/
app.post('/ingest', (req, res) => {
    console.log(`received stuff: ${JSON.stringify(req.body)}`);
    const scan = req.body;

    await pool.query("BEGIN");
    
    const scanQuery = await pool.query('insert into Scan (scanTime, placeId) values ($1, $2)', [scan.scanTime, scan.place]);
    const scanId = scanQuery.rows[0].id;

    const queries = scan.wifiAccessPoints.map(async ap => {
        const accessPointQuery = await pool.query(
            'insert into AccessPoint (name, macAddress, numConnectClients, scanId) values ($1, $2, $3, $4)', 
            [ap.name, ap.macAddress, ap.numConnectedClients, scanId]
            );
            
        const accessPointId = accessPointQuery.rows[0].id;

        const clients = ap.concreteDetectedClients.map(cl => {
            return [cl.macAddress, scanId, accessPointId];
        })

        await pool.query(format('insert into AccessPoint (macAddress, scanId, accessPointId) values %L', clients));
    });

    Promise.all(queries);
    await pool.query("COMMIT");
    
    res.send('OK');
})

app.listen(port, () => {
    console.log(`Ingest listening at port: ${port}`)
})
