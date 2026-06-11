# Transit Notification Engine

A distributed backend that polls live GTFS-RT transit APIs every 30 seconds,
detects vehicle delays, and sends automated alerts to subscribers via AWS SNS.
Built with Python, Celery, Redis, and Docker.

## How to Use

Start the engine:

```bash
docker-compose up --build
```

Run tests:

```bash
pytest tests/ -v
```

## How to Build and Install

**Requirements:** Docker Desktop, Python 3.11+

```bash
git clone https://github.com/SiddhantBhirud/Transit-Notification-Engine
cd transit-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your GTFS-RT API key and AWS credentials before running.

## Uninstall

```bash
docker-compose down
deactivate
cd ..
rm -rf transit-engine
```

## License

MIT — see [LICENSE](https://opensource.org/licenses/MIT)
