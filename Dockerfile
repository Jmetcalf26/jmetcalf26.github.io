FROM node:lts-alpine3.22

WORKDIR /usr/src/app

COPY package*.json ./
COPY requirements.txt ./

RUN npm ci\
&& apk update && apk add --no-cache python3 py3-pip \
&& mkdir -p ./.venvs/ && python3 -m venv ./.venvs/CONCERT \
&& . ./.venvs/CONCERT/bin/activate \
&& pip3 install -r requirements.txt
#RUN npm install && apk update && apk add --no-cache python3 py3-pip && . .venv/bin/activate

# If you are building your code for production
# RUN npm ci --omit=dev

COPY . .

EXPOSE 3000
CMD [ "node", "server.js" ]