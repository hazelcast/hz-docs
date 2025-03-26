private int findFreePort(int from) {
    for (int port = from; port < from + 100; port++) {
      try {
        new ServerSocket(port).close();
        return port;
      } catch (IOException e) {
        // port not available, try next
      }
    }
    throw new RuntimeException("Could not find an available port");
  }