import { useEffect, useState } from 'react';
import './App.css';
import {
    Container,
    ListGroup,
    Badge
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getPlaceStatus } from './utils';
import mqtt from 'mqtt';
import produce from 'immer';

function App() {
    const [occupancies, setOccupancies] = useState({})

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
                console.log(newOccupancies)

                const temp = produce(occupancies, draft => {
                    for (let placeId in newOccupancies) {
                        const { occupancy_percentage, confirmed_number } = newOccupancies[placeId];

                        if (placeId in draft) {
                            const prev = draft[placeId];
                            prev.occupancy_percentage = occupancy_percentage;
                            prev.confirmed_number = confirmed_number;
                        }
                    }
                });
                console.log(temp);
                setOccupancies(temp);
            }
        })

        async function fetchData() {
            const occupanciesRequest = await fetch("http://localhost:8089/occupancies")
            const occupanciesJson = await occupanciesRequest.json();
            console.log(occupanciesJson)

            if (!ignore) setOccupancies(occupanciesJson)
        }

        fetchData();

        return () => { 
            ignore = true;
            mqttClient.end();
        }
    }, []);

    return (
        <Container>
            <ListGroup>
                {Object.values(occupancies).map((place) => {
                    const placeStatus = getPlaceStatus(place.occupancy_percentage);

                    return (
                        <ListGroup.Item key={place.id}>
                            <Badge bg={placeStatus.bg}>{placeStatus.text} </Badge>
                            <Link to={`/place/${place.id}`}>
                                <span className="ps-5">
                                    {place.name} 
                                </span>
                            </Link>
                        </ListGroup.Item>
                    )
                })}
            </ListGroup>
        </Container>
    );
}

export default App;
