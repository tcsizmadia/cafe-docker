group "default" {
  targets = ["api-gateway", "backend", "cafe-db"]
}

variable "PYTHON_VERSION" {
  default = "3.13"
}

variable "BACKEND_INTERNAL_PORT" {
  default = "8000"
}

variable "BUILD_VERSION" {
  default = "0.0.1"
}

variable "RELEASE" {
  default = "0"
}

target "_common_backend" {
  build_args = {
    PYTHON_VERSION = "${PYTHON_VERSION}"
    PORT = "${BACKEND_INTERNAL_PORT}"
  }
}

target "backend" {
  inherits = [ "_common_backend" ]
  name = "${item.service}-service"
  context = "./${item.service}_service"
  dockerfile = "Dockerfile"
  platforms = item.platforms
  tags = [ "cafe-docker/${item.service}-service:latest", "cafe-docker/${item.service}-service:${BUILD_VERSION}" ]
  matrix = {
    item = [ 
      { 
        "service" = "loyalty", 
        "platforms" = equal("1", RELEASE) ? [ "linux/arm64", "linux/amd64" ] : [ "" ], 
      }, { 
        "service" = "menu", 
        "platforms" = equal("1", RELEASE) ? [ "linux/arm64", "linux/amd64" ] : [ "" ], 
      }, { 
        "service" = "pos", 
        "platforms" = equal("1", RELEASE) ? [ "linux/arm64", "linux/amd64" ] : [ "" ], 
      } 
    ]
  }
}


target "api-gateway" {
  context = "./api_gateway"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/api-gateway:latest", "cafe-docker/api-gateway:${BUILD_VERSION}"]
}


target "cafe-db" {
  context = "./cafe_db"
  dockerfile = "Dockerfile"
  tags = ["cafe-docker/cafe-db:latest", "cafe-docker/cafe-db:${BUILD_VERSION}"]
}

