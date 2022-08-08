for try in {1..300}; do
  echo "Attack $try"
  wget http://127.0.0.2:8080/login
done