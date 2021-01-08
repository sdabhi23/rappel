# Rappel

An idea management tool, inspired from kanban boards and integrated with GitHub

## Features

- Automatically sync your GitHub repos
- Sort the repos into 5 categories:
  1. Backlog
  2. Active
  3. Work In Progress
  4. Done
  5. Archive
- Add working notes for the repos directly inside their cards

## Roadmap

- Add notes for new ideas
- Filter repos
- Search repos
- Hide stale repos into a separate tab
- Automatically delete repos when they are deleted from GitHub
- Integration with PyPI and NPM
- Integration with GitLab

## Development

- Run the app locally using Docker

  ```bash
  ➜ docker run --rm -p 80:80 --env DJANGO_SECRET_KEY="-0cn(wy^w*!^ktl82_#%s)1p%90k8(8!8-yhhll5h1my13v3^#" rappel-tst
  ```

- Generate dependency lists from Pipfile.lock using [jq tool](https://stedolan.github.io/jq/)

  ```bash
  ➜ jq -r '.default | to_entries[] | .key + .value.version' Pipfile.lock > requirements.txt
  ➜ jq -r '.develop | to_entries[] | .key + .value.version' Pipfile.lock > requirements-dev.txt
  ```
