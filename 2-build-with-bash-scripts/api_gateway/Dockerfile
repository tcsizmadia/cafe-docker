FROM node:slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY ./app ./app

EXPOSE 8000
CMD ["node", "app/index.js"]
