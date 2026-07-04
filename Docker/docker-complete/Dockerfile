# Build stage
FROM node:26-alpine AS builder

WORKDIR /app

COPY package.json .

RUN npm install

# Runtime stage
FROM node:26-alpine

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY . .

EXPOSE 3000

CMD ["node", "app.mjs"]