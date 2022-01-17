import { useEffect, useState } from 'react';
import './App.css';
import {
    Container,
    Badge
} from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import {  getPlaceStatus } from './utils';
import mqtt from 'mqtt';
import {
    Line,
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
    const { placeId } = useParams();

    const [occupancy, setOccupancy] = useState(null)
    const [chartData, setChartData] = useState(null)

    useEffect(() => {
        let ignore = false

        let mqttClient = mqtt.connect('mqtt://localhost:9001', {clean: true, connectTimeout: 60000});
        mqttClient.on('connect', () => {
            console.log("Connected to PSOT MQTT broker");
            mqttClient.subscribe('occupancy_notifications');
        })
        mqttClient.on('reconnect', () => {
            console.log("Reconnected to PSOT MQTT broker");
            mqttClient.subscribe('occupancy_notifications');
        })
        mqttClient.on('message', (topic, message) => {
            if (topic === 'occupancy_notifications') {
                const newOccupancies = JSON.parse(message.toString())

                if (newOccupancies[placeId]) {
                    const { name, occupancy_percentage, confirmed_number } = newOccupancies[placeId]
                    const temp = {
                        name,
                        occupancy_percentage,
                        confirmed_number
                    }
                    console.log(temp);
                    setOccupancy(temp);
                }
            }
        })

        async function fetchData() {
            const occupancyRequest = await fetch(`http://localhost:8089/occupancies/${placeId}`)
            const occupancyJson = await occupancyRequest.json();
            console.log(occupancyJson)

            if (!ignore) setOccupancy(occupancyJson)
        }

        async function fetchHistory() {
            const historyRequest = await fetch(`http://localhost:8089/occupancies/${placeId}/history`)
            const historyJson = await historyRequest.json();
            console.log(historyJson)

            if (!ignore) {
                const data = {
                    labels: historyJson.records.map(record => record.time),
                    datasets: [
                        {
                            label: 'Occupancy Level',
                            data: historyJson.records.map(record => record.percentage)
                        }
                    ]
                }
                setChartData(data)
            }
        }

        fetchData();
        fetchHistory();

        return () => { 
            ignore = true;
            mqttClient.end();
        }
    }, [placeId]);

    const placeStatus = getPlaceStatus(occupancy ? occupancy.occupancy_percentage : 0)

    return occupancy ? 
        (
            <Container>
                <h1>{occupancy.name}</h1>
                <Badge bg={placeStatus.bg}>{placeStatus.text} </Badge>
                <span className="ps-5">
                Estimated {occupancy.confirmed_number} people at the location
                </span>
                { chartData ? (
                    <Line
                        data={chartData}
                        />
                ): null }
            </Container> 
        )
        : 'Loading...' ;
}

export default App;
