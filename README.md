# Project Chupacabra
#### A Simple Online Game Backend in Python

The story of this package started with a simple idea. Gaming websites have been on the web basically since there has been a web. How might someone go about designing and building a backend for a simple gaming website? 
What would the public API look like? What about the overall backend architecture. 
As I build this project, I hope to build a system that answers these questions in a way that is simple enough to be able to clearly explain my choices.

I make no promises about performance or security, so I wouldn't use this in a real website. But, it will hopefully work on a laptop and could maybe even be used to play games on a local network. Again, the idea of this is to build a working tutorial not to build a full enterprise solution.

## Architecture
The basic architecture should be as follows:

### Chupacabra server
This is server for the main public API. A user should
be sending reqeusts to this server. Its responsibilities will
be
 1) Handling any user session authentication
 2) Knowing what games exist in the backend
 3) Passing data from users to the games
 
### Chupacabra client
This provides a standalone package for use by a frontend
or for a user to hit when communicating with the server.

### Game servers
Game servers will be internal servers that should only be
communicating with other internal servers and with the main
Chupacabra server.

There is a common API for the game servers to use but other
than that, they will be left to their own devices
to figure out how to implement a game.

## Current Functionality

At present the functionality is still somewhat limited.
 1) A simple main server that handles authentication
 2) A server for two-player games of Tic Tac Toe

This can be easily deployed with `docker-compose`:
```bash
cd chupacabra
docker-compose up --build 
```

And then the server will be available at `localhost:7653`.

## Future Improvements
 1) More documentation & examples. I haven't added much yet.
 2) More extensive unit testing and end-to-end testing
 3) Game result databases, possibly game move databases
 4) More properly defined clients
 5) More user-oriented endpoints (logout, change password)
 6) mypy support

## FAQ
 
 1) **Q:** Why call it chupacabra? **A:** Why not?
 2) **Q:** Does it stand for anything? **A:** No, not really
 2) **Q:** Can I use this at work without getting caught? **A:** I wouldn't recommend it.
 3) **Q:** Is this useful for a real web backend? **A:** I would strongly recommend against deploying this in the wild, as I have not tried to actually make sure that anything here is secure.
 4) **Q:** So then what is it useful for? **A:** I see this as more of a tutorial about how to design something like this. That said, I'm also a physicist so that doesn't mean that it'll work as well as the many actual gaming websites that exist.
