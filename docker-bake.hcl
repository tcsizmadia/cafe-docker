group "default" {
  targets = ["api-gateway", "loyalty-service", "menu-service", "pos-service", "cafe-db"]
}

target "api-gateway" {
  context = "./api_gateway"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/api-gateway:latest", "cafe-docker/api-gateway:0.0.1"]
}

target "loyalty-service" {
  context = "./loyalty_service"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/loyalty-service:latest", "cafe-docker/loyalty-service:0.0.1"]
}

target "menu-service" {
  context = "./menu_service"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/menu-service:latest", "cafe-docker/menu-service:0.0.1"]
}
target "pos-service" {
  context = "./pos_service"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/pos-service:latest", "cafe-docker/pos-service:0.0.1"]
}
target "cafe-db" {
  context = "./cafe_db"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/cafe-db:latest", "cafe-docker/cafe-db:0.0.1"]
}