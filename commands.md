## Commands

- docker network inspect bridge
- docker run -d -p 3000:3000 --name=grafana -v grafana-storage:/var/lib/grafana grafana/grafana-enterprise
- docker run -it --rm -d -v /Users/gandharva/dev/vm-data:/victoria-metrics-data -p 8428:8428 -p 4242:4242 victoriametrics/victoria-metrics -opentsdbListenAddr=:4242