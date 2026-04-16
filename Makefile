.PHONY: build run stop test test-go test-python clean

# Build all containers
build:
	docker-compose build

# Run the full stack locally
run:
	docker-compose up --build -d

# Stop all services
stop:
	docker-compose down

# Run all tests
test: test-go test-python

# Run Go tests for environment service
test-go:
	cd environment_service && go test ./... -v

# Run Python tests for routing engine
test-python:
	cd routing_engine && python -m pytest tests/ -v

# Deploy to Kubernetes
deploy:
	kubectl apply -f k8s/

# Remove Kubernetes deployment
undeploy:
	kubectl delete -f k8s/

# Clean build artifacts
clean:
	docker-compose down -v --rmi local
	cd frontend && rm -rf node_modules build
	cd routing_engine && rm -rf __pycache__ .pytest_cache
