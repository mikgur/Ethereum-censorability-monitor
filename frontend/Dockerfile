FROM node:18.14.2

WORKDIR /frontend
COPY . .

EXPOSE 5173

RUN npm install --force
ENTRYPOINT npm run dev