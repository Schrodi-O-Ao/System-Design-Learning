# System Design Practice

A personal learning project. Building system design problems from scratch
using Python and FastAPI, working through them by difficulty.

Not production code. Not a tutorial. Just me learning by building. Feel Free to use it as a guide or to copy it.

## What's being built

### Easy
- [x] URL shortener
- [ ] Pastebin
- [ ] File upload service
- [ ] Rate limiter

### Medium
- [ ] Notification service
- [ ] Chat system
- [ ] Job/task queue
- [ ] Web crawler
- [ ] News feed
- [ ] Metrics/logging service

## Stack
- Python
- FastAPI
- SQLite (for local dev)
- Redis (where needed)
- Uvicorn

## Running
```bash
pip install -r requirements.txt
uvicorn <module>:app --reload