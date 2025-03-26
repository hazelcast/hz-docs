context.vertx()
  .sharedData()
  .getCounter("requestId")
  .onSuccess(counter -> {
    counter.incrementAndGet()
      .onSuccess(requestId -> {
        context.json(
          new JsonObject()
            .put("requestId", requestId)
            .put("messages", messages)
        );
      });
  });