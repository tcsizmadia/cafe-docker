# Café Docker - Microservices Demo Project

This is a demonstration project designed to help interns learn how Docker Compose orchestrates containers in a microservices architecture. The project simulates a café management system with three interconnected services.

## Project Overview

This project demonstrates how to build and connect multiple microservices using Docker and Docker Compose. Each service runs in its own container and communicates with others through a shared network.

### Services Architecture

The application consists of four main services:

1. **API Gateway Service** (Port 8000)
   - Central entry point for all client requests
   - Routes requests to appropriate microservices
   - Provides a unified API interface to clients

2. **Loyalty Card Service** (Port 8001)
   - Manages customer profiles
   - Tracks loyalty points
   - Allows redeeming points for discounts

3. **Menu Service** (Port 8002)
   - Provides information about available menu items
   - Contains item details (name, description, price)

4. **POS (Point of Sale) Integration Service** (Port 8003)
   - Handles transactions
   - Communicates with both Loyalty and Menu services
   - Applies loyalty points to orders

Each service has its own:
- Containerized environment with specific dependencies
- Independent API endpoints
- Logical database schema within the shared PostgreSQL instance
- Clear responsibilities within the system

## Prerequisites

Before starting, ensure you have the following installed on your system:
- Docker (20.10.x or newer)
- Docker Compose (2.x or newer)

You can verify your installation with:
```bash
docker --version
docker-compose --version
```

## Getting Started

### Clone the Repository
```bash
git clone <repository-url>
cd cafe-docker
```

### Building and Running with Docker Bake

This project now uses Docker Bake for a more efficient and configurable build process. A convenient wrapper script has been provided to simplify common operations.

#### Using the Helper Script

The `cafe-docker.sh` script provides an easy way to build and run the application:

```bash
# Make the script executable (first time only)
chmod +x ./cafe-docker.sh

# View available commands
./cafe-docker.sh help

# Build all services (defaults to YAML format)
./cafe-docker.sh build

# Choose between YAML or HCL format
./cafe-docker.sh build -f yaml    # Use YAML format (default)
./cafe-docker.sh build -f hcl     # Use HCL format

# Build only specific service group
./cafe-docker.sh build -t api    # API Gateway only
./cafe-docker.sh build -t backend # All backend services

# Build with a specific tag
./cafe-docker.sh build --tag v1.0

# Build and start all services
./cafe-docker.sh up

# Stop all services
./cafe-docker.sh down

# View logs
./cafe-docker.sh logs
```

#### Manual Docker Bake Commands

If you prefer to use Docker Bake directly:

```bash
# Build all services using YAML format (preferred)
docker buildx bake -f docker-bake.yaml

# Build all services using HCL format
docker buildx bake -f docker-bake.hcl

# Build specific target group
docker buildx bake -f docker-bake.yaml api
docker buildx bake -f docker-bake.yaml backend

# Build with custom tag
docker buildx bake -f docker-bake.yaml --set "*.args.TAG=v1.0"

# Build and load images to local Docker
docker buildx bake -f docker-bake.yaml --load
```

### Legacy Docker Compose Commands

You can still use Docker Compose directly if preferred:

```bash
# Start all services
docker-compose up

# Run in detached mode
docker-compose up -d

# View logs from all services
docker-compose logs

# View logs from a specific service
docker-compose logs loyalty-service
docker-compose logs menu-service
docker-compose logs pos-service

# Stop the application
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## API Endpoints

### API Gateway (http://localhost:8000)
- `GET /` - Gateway welcome message and service availability
- All endpoints below are accessible through the gateway

### Loyalty Card Service (http://localhost:8001)
- `GET /` - Service welcome message
- `POST /customers` - Create a new customer
- `GET /customers/{customer_id}` - Get customer details
- `GET /customers/{customer_id}/points` - Check loyalty points
- `POST /customers/{customer_id}/points` - Add/subtract loyalty points

### Menu Service (http://localhost:8002)
- `GET /` - Service welcome message
- `GET /menu` - Get all menu items
- `GET /menu/{item_id}` - Get specific menu item details

### POS Service (http://localhost:8003)
- `GET /` - Service welcome message
- `POST /transactions` - Create a new transaction
- `GET /transactions/{transaction_id}` - Get transaction details
- `POST /transactions/{transaction_id}/apply_loyalty` - Apply loyalty points to transaction

## Sample Usage Flow

Here's a typical workflow to test the system:

1. **Create a customer**
```bash
# Using the API Gateway:
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Or directly using the Loyalty Service:
curl -X POST http://localhost:8001/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

2. **Check menu items**
```bash
# Using the API Gateway:
curl http://localhost:8000/menu

# Or directly using the Menu Service:
curl http://localhost:8002/menu
```

3. **Create a transaction** (replace customer_id and item_id with actual values)
```bash
# Using the API Gateway:
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [
      {"item_id": 1, "quantity": 2},
      {"item_id": 3, "quantity": 1}
    ]
  }'

# Or directly using the POS Service:
curl -X POST http://localhost:8003/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [
      {"item_id": 1, "quantity": 2},
      {"item_id": 3, "quantity": 1}
    ]
  }'
```

4. **Apply loyalty points** (replace with actual transaction_id)
```bash
# Using the API Gateway:
curl -X POST http://localhost:8000/transactions/1/apply_loyalty \
  -H "Content-Type: application/json" \
  -d '{"points_to_use": 10}'

# Or directly using the POS Service:
curl -X POST http://localhost:8003/transactions/1/apply_loyalty \
  -H "Content-Type: application/json" \
  -d '{"points_to_use": 10}'
```

## Docker Compose Concepts Demonstrated

This project showcases several important Docker Compose concepts:

1. **Multi-container applications**: Running multiple services together
2. **Service discovery**: Services can call each other by service name
3. **Environment variables**: Configuring services through environment variables
4. **Volume management**: Persisting database data across container restarts
5. **Network configuration**: Services communicate over a shared network
6. **Dependency management**: Services wait for dependencies before starting
7. **Port mapping**: Exposing internal service ports to the host machine

## Project Structure

```
cafe-docker/
├── docker-compose.yml        # Main orchestration file
├── README.md                 # Project documentation
│
├── api_gateway/              # API Gateway Service
│   ├── Dockerfile            # Container configuration
│   ├── requirements.txt      # Python dependencies
│   └── app/
│       └── main.py           # FastAPI application code
│
├── loyalty_service/          # Loyalty Card Service
│   ├── Dockerfile            # Container configuration
│   ├── requirements.txt      # Python dependencies
│   └── app/
│       └── main.py           # FastAPI application code
│
├── menu_service/             # Menu Service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── main.py
│
└── pos_service/              # POS Integration Service
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        └── main.py
```

## Architecture Diagram

```mermaid
graph TD
    subgraph "Docker Network"
        subgraph "Database Container"
            DB[(PostgreSQL)]
            DB_LOYALTY[(loyalty_db)]
            DB_MENU[(menu_db)]
            DB_POS[(pos_db)]
            DB --- DB_LOYALTY
            DB --- DB_MENU
            DB --- DB_POS
        end
        
        subgraph "Microservices"
            GATEWAY[API Gateway<br>:8000]
            LOYALTY[Loyalty Service<br>:8001]
            MENU[Menu Service<br>:8002]
            POS[POS Integration<br>Service<br>:8003]
        end
        
        %% Database connections
        LOYALTY --- DB_LOYALTY
        MENU --- DB_MENU
        POS --- DB_POS
        
        %% Service interactions
        GATEWAY -->|Forward Requests| LOYALTY
        GATEWAY -->|Forward Requests| MENU
        GATEWAY -->|Forward Requests| POS
        POS -->|Get Customer<br>Add Points| LOYALTY
        POS -->|Get Menu Items| MENU
        
        %% External access
        CLIENT((Client))
        CLIENT -.->|API Requests| GATEWAY
        CLIENT -.->|Direct API<br>Requests| LOYALTY
        CLIENT -.->|Direct API<br>Requests| MENU
        CLIENT -.->|Direct API<br>Requests| POS
    end    
```

## Database Schema

The application uses a single PostgreSQL container (`cafe-db`) that hosts three separate logical databases:

### Loyalty Service DB (loyalty_db)
- `customers` table: Stores customer information
- `loyalty_points` table: Tracks points for each customer

### Menu Service DB (menu_db)
- `menu_items` table: Stores information about available food and drinks

### POS Service DB (pos_db)
- `transactions` table: Records of all transactions with item details

All databases share the same PostgreSQL instance but are logically separated, allowing each service to maintain its own data while simplifying the infrastructure requirements.

## Learning Objectives

Through this project, you should gain an understanding of:

- How containers isolate application code and dependencies
- How Docker Compose manages multi-container applications
- How microservices communicate with each other
- Basic patterns for service discovery in containerized environments
- Database persistence with Docker volumes
- Environment-based configuration in Docker

## Troubleshooting

### Common Issues

1. **Services can't connect to databases**
   - Check if database containers are running: `docker-compose ps`
   - Verify network connectivity: `docker network inspect cafe-network`

2. **Changes not reflected after rebuild**
   - Force rebuild: `docker-compose up --build`
   - Remove all containers and volumes: `docker-compose down -v` then `docker-compose up`

3. **Port conflicts**
   - Check if ports are already in use: `lsof -i :<port>` (Unix/Mac) or `netstat -ano | findstr :<port>` (Windows)
   - Change the mapped ports in docker-compose.yml

## Extensions and Challenges

Once you're comfortable with the basic setup, try these extensions:

1. Add a web frontend service that connects to the API services
2. Implement authentication and authorization
3. Add automated tests for the services
4. Set up continuous integration/continuous deployment
5. Implement message queuing between services using RabbitMQ or Kafka

## Resources for Learning More

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Microservices Architecture Pattern](https://microservices.io/patterns/microservices.html)
- [12 Factor App Methodology](https://12factor.net/)