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
   git clone git@github.com:zejj42/stock-quote-api.git
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

## Switching Between Different Branches with Docker

To switch between different branches of the repository and run the application using Docker, the following steps ensure a seamless transition:

### Steps

1. Switch to the desired Git branch:

   ```bash
   git checkout <branch_name>
   ```

2. Stop all running containers, rebuild Docker images, and start the services:

   ```bash
   docker-compose down && docker-compose build && docker-compose up
   ```

   **Note**: Executing these commands will reset any existing cache.

## Cache Strategy

The service employs a dynamic cache strategy using Redis to store stock data. The cache expiration time is determined by the stock's volatility and trading hours, thereby minimizing unnecessary API calls while ensuring updated stock information.

## Cache Interface (`cache_interface`)

The cache interface abstracts the caching mechanism, facilitating the integration of different caching backends such as Redis or in-memory solutions without altering the core application code.

## Stock API Interface (`stock_api`)

The stock API interface offers an abstraction for stock data retrieval, allowing for the utilization of various stock API providers without significant code modifications. Configuration updates are all that is required to switch between API providers.

## Type Hinting

Python's type hinting features are extensively used throughout the codebase to enhance code readability, enable better development-time error checking, and simplify debugging.

## Rate Limiting (Only in `rate-limited` branch)

In addition to the main features, the `rate-limited` branch includes functionality to limit the number of API requests based on the source IP. This is to ensure that the API is not overused.

### Limitation Rules

- Up to 10 requests per minute per IP for the `/quote/<symbol>` endpoint.

### Handling Exceeding Limits

If a specific IP source exceeds the limit, the service will return a `429 Too Many Requests` status code.

## Handling of Sensitive Information

In this codebase, API keys and other confidential configurations are directly embedded within the `configurations.py` file. In a production-grade application, it's essential to store these sensitive pieces of information as environment variables or utilize a secure secret management service to prevent potential exposure.
