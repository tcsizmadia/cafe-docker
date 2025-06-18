const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const { createProxyMiddleware } = require("http-proxy-middleware");
const swaggerUi = require("swagger-ui-express");
const yaml = require("js-yaml");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 8000;

// Service URLs from environment variables with fallbacks
const LOYALTY_SERVICE_URL =
  process.env.LOYALTY_SERVICE_URL || "http://loyalty-service:8000";
const MENU_SERVICE_URL =
  process.env.MENU_SERVICE_URL || "http://menu-service:8000";
const POS_SERVICE_URL =
  process.env.POS_SERVICE_URL || "http://pos-service:8000";

// CORS and Helmet configurations
app.use(cors());
app.use(helmet());

// Load OpenAPI specification
const openApiPath = path.join(__dirname, "openapi.yaml");
const openApiSpec = yaml.load(fs.readFileSync(openApiPath, "utf8"));

// API Documentation routes - only use Swagger UI
app.use("/docs", swaggerUi.serve, swaggerUi.setup(openApiSpec));

// Serve the OpenAPI spec as JSON
app.get("/api-spec", (req, res) => {
  res.json(openApiSpec);
});

// Root endpoint
app.get("/", (req, res) => {
  res.json({
    message: "Welcome to the Cafe API Gateway",
    services: {
      loyalty: LOYALTY_SERVICE_URL,
      menu: MENU_SERVICE_URL,
      pos: POS_SERVICE_URL,
    },
  });
});

// Error handling for proxy requests
const handleProxyError = (err, req, res, serviceName) => {
  console.error(`${serviceName} service error:`, err);
  res
    .status(503)
    .json({ detail: `${serviceName} service unavailable: ${err.message}` });
};

// Configure proxy middleware for each service
app.use(
  "/menu",
  createProxyMiddleware({
    target: MENU_SERVICE_URL,
    changeOrigin: true,
    onError: (err, req, res) => handleProxyError(err, req, res, "Menu"),
    pathRewrite: { "^/menu": "/menu" },
  })
);

app.use(
  "/customers",
  createProxyMiddleware({
    target: LOYALTY_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { "^/customers": "/customers" },
    onError: (err, req, res) => handleProxyError(err, req, res, "Loyalty"),
  })
);

app.use(
  "/transactions",
  createProxyMiddleware({
    target: POS_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { "^/transactions": "/transactions" },
    onError: (err, req, res) => handleProxyError(err, req, res, "POS"),
  })
);

// Global error handler
app.use((err, req, res, next) => {
  console.error("Global error handler:", err);
  res.status(500).json({ detail: "Internal server error" });
});

// Start the server
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`Proxying to services:
  - Loyalty: ${LOYALTY_SERVICE_URL}
  - Menu: ${MENU_SERVICE_URL}
  - POS: ${POS_SERVICE_URL}
  `);
});
