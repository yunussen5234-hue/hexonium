FROM node:20-alpine
WORKDIR /app
COPY package.json .
ARG NPM_REGISTRY=https://registry.npmjs.org/
RUN npm config set registry ${NPM_REGISTRY} \
 && npm config set fund false \
 && npm config set audit false \
 && npm install --no-audit --no-fund --progress=false
COPY . .
CMD ["npm", "run", "dev"]
