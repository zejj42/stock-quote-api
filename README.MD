# Stock Quote API

A RESTful API service built using Flask to fetch real-time stock quotes. This service makes use of Alpha Vantage's API to fetch stock data and caches the results in Redis to improve performance and reduce costs. The service is containerized using Docker.

## Table of Contents

- [Features](#features)
- [Branches](#branches)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Authentication](#authentication)
- [Cache Strategy](#cache-strategy)
- [Rate Limiting](#rate-limiting) (Only in `rate-limited` branch)

## Features

- Fetch real-time stock quotes
- Utilizes Redis for caching
- API Key Authentication for admin routes
- Dynamic cache expiration based on stock volatility

## Branches

- `main`: Contains only the basic requirements (features 1-4).
- `rate-limited`: Includes the additional feature of IP rate limiting (feature 5).

## Installation

### Prerequisites

- Docker

### Steps

1. Clone the repository:
   ```bash
   git@github.com:zejj42/stock-quote-api.git
   ```
2. Navigate to the project directory:
   ```bash
   cd stock-quote-api
   ```
3. Start the Docker containers:
   ```bash
   docker-compose up
   ```

## Usage

To fetch a stock quote:

```bash
curl -X GET http://localhost:5001/quote/AAPL
```

To check the cost counter (Admin only):

```bash
curl -X GET http://localhost:5001/cost -H "x-api-key: k78a0snbf8JHm"
```

To reset cost counter (Admin only):

```bash
curl -X POST http://localhost:5001/reset_cost -H "x-api-key: k78a0snbf8JHm"
```

## Endpoints

- `GET /quote/<symbol>`: Fetches the real-time stock quote for a given stock symbol.
- `GET /cost`: Fetches the total API cost incurred. (Admin only)
- `POST /reset_cost`: Resets the cost counter. (Admin only)

## Authentication

The `/cost` and `/reset_cost` endpoints require an admin API key to be included in the request headers as `x-api-key`.

## Cache Strategy

The service employs a dynamic cache strategy using Redis to store stock data. The cache expiration time is determined by the stock's volatility.

## Rate Limiting (Only in `rate-limited` branch)

In addition to the main features, the `rate-limited` branch includes functionality to limit the number of API requests based on the source IP. This is to ensure that the API is not overused.

### Limitation Rules

- Up to 10 requests per minute per IP for the `/quote/<symbol>` endpoint.

### Handling Exceeding Limits

If a specific IP source exceeds the limit, the service will return a `429 Too Many Requests` status code.
