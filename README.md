# 🚁 UAV Flight Optimizer

A highly scalable pathfinding engine designed to generate energy-optimized 3D flight routes for Unmanned Aerial Vehicles (UAVs). By integrating real-time weather data, high-resolution topography, and strict airspace geofences, this system calculates the most efficient path based on advanced aerodynamic profiling and a custom energy-weighted routing algorithm.

## 📑 Table of Contents
- [Features](#-features)
- [Architecture & Technologies](#-architecture--technologies)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

* **🔋 Energy-Weighted Pathfinding:** Employs a custom 3D A* algorithm weighted by calculated energy consumption (Joules/second) rather than relying solely on the shortest geographic distance.
* **🌤️ Real-Time Environment Awareness:** Automatically polls NOAA/OpenWeather for 3D wind vectors and parses heavy GeoTIFF/SRTM tiles to account for terrain elevation and slopes.
* **🛑 Airspace Compliance:** Caches FAA no-fly zones and Temporary Flight Restrictions (TFRs) to actively route around dynamic geofences.
* **🚁 Advanced Aerodynamic Modeling:** Calculates drag forces and thrust requirements using specific drone profiles (mass, frontal area, drag coefficient, and battery capacity).
* **🗺️ Interactive Mission Planner:** A robust web dashboard featuring MapboxGL for 3D trajectory visualization, alongside 2D charts tracking altitude vs. terrain height and estimated battery drain.
* **☸️ Cloud-Native Scalability:** Built on a microservices architecture, fully containerized, and optimized for Kubernetes orchestration with Redis caching.

## 🛠️ Architecture & Technologies

The system is separated into three distinct, containerized microservices:

1. **Environment Service (Go):** A high-concurrency internal gRPC/REST server that fetches spatial maps, weather grids, and airspace constraints.
2. **Routing Engine (Python / FastAPI):** The physics and mathematics brain. It utilizes `networkx`, `shapely`, and `scipy` to build searchable 3D graph nodes and process aerodynamic drag constraints.
3. **Frontend (React / TypeScript):** The user-facing mission planner utilizing `mapbox-gl`, `turf.js`, and `recharts` for an interactive map and drag-and-drop waypoint experience.

## 📋 Prerequisites

* Docker and Docker Compose (for local development)
* Kubernetes cluster (for production deployment)
* Mapbox API Key (required for frontend rendering)
* Node.js, Go 1.20+, and Python 3.10+ (for bare-metal development)

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mtepenner/uav-flight-optimizer.git](https://github.com/mtepenner/uav-flight-optimizer.git)
   cd uav-flight-optimizer
   ```

2. **Configure Environment Variables:**
   Create `.env` files in the respective service directories to provide your Mapbox and Weather API keys.

3. **Deploy Locally via Docker Compose:**
   The included `docker-compose.yml` sets up the local cluster along with the Redis cache.
   ```bash
   make run # Or explicitly: docker-compose up --build -d
   ```

4. **Deploy via Kubernetes:**
   Apply the provided manifests for orchestration in a cloud environment.
   ```bash
   kubectl apply -f k8s/
   ```

## 💻 Usage

Once the cluster is actively running:

1. Navigate to the frontend Mission Planner at `http://localhost:3000`.
2. Select your specific drone profile (e.g., Quadcopter vs. Fixed Wing) to set baseline aerodynamic parameters.
3. Use the MapboxGL interface to drop a starting point and a destination waypoint.
4. Click **Optimize Route**. The frontend will fetch the computed GeoJSON trajectory and render it over the topological map.
5. Review the **Elevation Profile** and **Battery Curve** charts below the map to verify the drone has sufficient energy to safely complete the mission.

## 🤝 Contributing

Contributions to improve pathfinding efficiency or expand environment data sources are welcome! 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/NewAlgorithm`)
3. Ensure all unit tests pass, especially the A*/Dijkstra algorithms in the CI pipeline (`test-pathfinding.yml`) and container builds (`build-containers.yml`).
4. Commit your changes (`git commit -m 'Add a NewAlgorithm'`)
5. Push to the branch (`git push origin feature/NewAlgorithm`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
