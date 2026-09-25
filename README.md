# Amazon Copy Project

Portfolio Django marketplace project.

Production is deployed from GitHub by the server. Every new commit on `main`
is picked up by the server-side deploy timer and rebuilt with Docker Compose,
including the committed `amazon/db.sqlite3`.
