import { useEffect, useState } from 'react';
import './App.css';
import {
    Container,
    ListGroup,
    Badge
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getPlaceStatus } from './utils';

function App() {
    const [occupancies, setOccupancies] = useState({})

    useEffect(() => {
        let ignore = false

        async function fetchData() {
            const occupanciesRequest = await fetch("http://localhost:8089/occupancies")
            const occupanciesJson = await occupanciesRequest.json();
            console.log(occupanciesJson)

            if (!ignore) setOccupancies(occupanciesJson)
        }

        fetchData();

        return () => { ignore = true; }
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
