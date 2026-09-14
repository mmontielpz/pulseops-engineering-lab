.PHONY: bootstrap verify dev seed clean

bootstrap:
	./scripts/bootstrap.sh

verify:
	./scripts/verify.sh

dev:
	./scripts/dev.sh

seed:
	backend/.venv/bin/python -m app.seed 2>/dev/null || (cd backend && python3 -m app.seed)

clean:
	rm -f backend/pulseops.db
	rm -rf frontend/dist
