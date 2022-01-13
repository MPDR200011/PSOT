import express from 'express';
import pg from 'pg';
import format from 'pg-format';

const { Pool } = pg;

const pool = new Pool({
    user: 'jeronimo',
    host: 'psot_db',
    database: 'psot_info',
    password: 'password123',
    port: 5432,
})

const app = express();
const port = 80;

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
app.post('/ingest', async (req, res) => {
    console.log(`received stuff: ${JSON.stringify(req.body)}`);
    const scan = req.body;

    const scanQuery = await pool.query('insert into scan (scan_time, place_id) values ($1, $2) RETURNING *', [scan.scanTime, scan.place]);
    const scanId = scanQuery.rows[0].id;

    const queries = scan.wifiAccessPoints.map(async ap => {
        const accessPointQuery = await pool.query(
            'insert into access_point (name, mac_address, num_connected_clients, scan_id) values ($1, $2, $3, $4) RETURNING *', 
            [ap.name, ap.macAddress, ap.numConnectedClients, scanId]
            );
            
        const accessPointId = accessPointQuery.rows[0].id;

        const clients = ap.concreteDetectedClients.map(cl => {
            return [cl.macAddress, scanId, accessPointId];
        })

        if (clients.length > 0) {
            await pool.query(format('insert into client (mac_address, scan_id, access_point_id) values %L', clients));
        }
    });

    Promise.all(queries);
    
    res.send('OK');
})

app.listen(port, () => {
    console.log(`Ingest listening at port: ${port}`)
})
