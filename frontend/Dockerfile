FROM node:18.14.1

WORKDIR /frontend
COPY . .

EXPOSE 5173

RUN npm install
ENTRYPOINT npm run dev