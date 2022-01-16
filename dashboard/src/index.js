import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import Place from './Place';
import reportWebVitals from './reportWebVitals';
import {
    BrowserRouter,
    Routes,
    Route
} from 'react-router-dom';

import 'bootstrap/dist/css/bootstrap.min.css';

ReactDOM.render(
    <React.StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<App/>}/>
                <Route path="/place/:placeId" element={<Place/>}/>
            </Routes>
        </BrowserRouter>
    </React.StrictMode>,
    document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
