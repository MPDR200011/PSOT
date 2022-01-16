import { useEffect, useState } from 'react';
import './App.css';
import {
    Container,
    Badge
} from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import {  getPlaceStatus } from './utils';

function App() {
    const { placeId } = useParams();

    const [occupancy, setOccupancy] = useState(null)

    useEffect(() => {
        let ignore = false

        async function fetchData() {
            const occupancyRequest = await fetch(`http://localhost:8089/occupancies/${placeId}`)
            const occupancyJson = await occupancyRequest.json();
            console.log(occupancyJson)

            if (!ignore) setOccupancy(occupancyJson)
        }

        fetchData();

        return () => { ignore = true; }
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
            </Container> 
        )
        : 'Loading...' ;
}

export default App;
