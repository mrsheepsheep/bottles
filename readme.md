# Bottles

A self-hosted alternative to Beeceptor, httpbin, requestbin...

To access the bottle UI, point your browser to `/ui`.

Bottles endpoints start with `/bottle/<id>`.

Features :
* GET, POST methods
* Custom HTTP headers
* Live bottle updates via Websockets
* Beeceptor-like live request viewer ('Mailbox')
* Vuetify app hosted inside the API (sketchy but it works like a charm)

ToDo :
* Websockets refactoring
* Vue Router for navigation
* Authentication with environment secret

If deploying on Heroku, use the http protocol as no SSL proxy is provided with this app.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/mrsheepsheep/bottles/tree/heroku-one-click)