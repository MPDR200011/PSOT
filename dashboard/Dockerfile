FROM node:17-alpine

COPY . /app/

WORKDIR /app

RUN npm install
RUN npm install -g webpack webpack-cli
RUN cd node_modules/mqtt && npm install . && webpack ./mqtt.js --output-library mqtt

RUN npm run build

CMD npm run serve
