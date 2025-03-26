  public void start() {
    // Create a Router
    Router router = router(vertx);

    // Create local SessionStore
    SessionStore store = LocalSessionStore.create(vertx);

    // Use the SessionStore to handle all requests
    router.route()
      .handler(SessionHandler.create(store));

    router.route(HttpMethod.PUT, "/").handler(context -> {
      context.request().bodyHandler(body -> {
        List<String> messages = getMessagesFromSession(context);

        JsonObject json = body.toJsonObject();
        String message = json.getString("message");
        messages.add(message);

        putMessagesToSession(context, messages);

        context.json(
          new JsonObject()
            .put("messages", messages)
        );
      });
    });

    // Create the HTTP server
    vertx.createHttpServer()
      // Handle every request using the router
      .requestHandler(router)
      // Start listening
      .listen(8888)
      // Print the port
      .onSuccess(server ->
        System.out.println(
          "HTTP server started on port " + server.actualPort()
        )
      );
  }

  private static List<String> getMessagesFromSession(RoutingContext context) {
    String messages = context.session().get("messages");
    if (messages == null) {
      return new ArrayList<>();
    } else {
      return new ArrayList<>(Arrays.asList(messages.split(",")));
    }
  }

  private void putMessagesToSession(RoutingContext context, List<String> messages) {
    context.session().put("messages", String.join(",", messages));
  }