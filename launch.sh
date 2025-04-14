#!/bin/bash

minikube delete
minikube start --driver=docker --cpus=2 --memory=4096
eval $(minikube docker-env)

cd app
docker build -t flask-app:latest .
cd ..

kubectl apply -f k8s/redis-deployment.yaml
kubectl wait --for=condition=available deployment/redis --timeout=180s
kubectl apply -f k8s/flask-deployment.yaml

echo "Waiting for application to start..."
for i in {1..30}; do
    POD_STATUS=$(kubectl get pod -l app=flask-app -o jsonpath='{.items[0].status.phase}')
    if [ "$POD_STATUS" == "Running" ]; then
        echo "Application is running!"
        break
    fi
    echo "Waiting for pod to start... (attempt $i/30)"
    sleep 5
done

kubectl get pods -o wide
echo "Service URL: $(minikube service flask-app --url)"