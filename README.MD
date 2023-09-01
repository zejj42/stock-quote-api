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

1. Clone the repository
2. Navigate to the project directory
3. Start the Docker containers:
   ```bash
   docker-compose up
   ```

## Usage

To fetch a stock quote:

```bash
curl -X GET http://localhost:5001/quote/AAPL
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
