...
int port = findFreePort(8888);

// Create the HTTP server
vertx.createHttpServer()
  // Handle every request using the router
  .requestHandler(router)
  // Start listening
  .listen(port)
...