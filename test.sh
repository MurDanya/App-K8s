sudo apt-get update && sudo apt-get install -y jq

SERVICE_URL=$(minikube service flask-app --url)
echo "Service URL: $SERVICE_URL"

echo -e "\nAnime list:"
curl -sS "$SERVICE_URL/list" | jq
