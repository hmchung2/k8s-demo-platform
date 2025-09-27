# k8s-demo-platform

쿠버네티스 환경에서 간단한 웹 애플리케이션(FastAPI)과 PostgreSQL DB를 배포하는 데모 프로젝트입니다.  
`app/`에는 애플리케이션 코드, `k8s/`에는 쿠버네티스 매니페스트를 두어 **앱 코드와 인프라 리소스**를 한 리포 안에서 분리 관리합니다.

- FastAPI + PostgreSQL
- Kubernetes 리소스: Deployment, Service, Ingress, ConfigMap, Secret, PVC, HPA, CronJob
- 로컬 실행 환경: kind + ingress-nginx

---

## Quickstart

```bash
# 1) kind 클러스터 생성 (Ingress 포트 매핑 포함)
cat > kind-ingress.yaml <<'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    listenAddress: 127.0.0.1
  - containerPort: 443
    hostPort: 443
    listenAddress: 127.0.0.1
EOF

kind create cluster --name demo --config kind-ingress.yaml

# 2) Ingress Controller 배포
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait deploy/ingress-nginx-controller --for=condition=Available --timeout=180s

# 3) 애플리케이션 이미지 빌드 & kind 클러스터에 로드
cd app
docker build -t demo/app:0.1 .
kind load docker-image demo/app:0.1 --name demo
cd ..

# 4) 매니페스트 적용
kubectl apply -f k8s/ns.yaml
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/db.yaml
kubectl apply -f k8s/app.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/cron.yaml

# 5) /etc/hosts에 도메인 매핑
echo "127.0.0.1 app.local" | sudo tee -a /etc/hosts

# 6) 서비스 접속 확인
curl http://app.local/stats
# {"hits":1,"env":"local"}
```

**Notes**

- 앱은 stateless, Postgres는 PVC로 데이터 영속
- Ingress에서 rewrite-target 어노테이션을 제거해야 /stats 경로가 정상 동작
- kind 클러스터를 지우고 다시 만들면 docker build + kind load를 다시 실행해야 함
- GitOps 확장: ArgoCD Application 리소스를 추가하면 배포 자동화 가능
- CronJob은 initContainer에서 pg_isready로 DB 준비를 확인 후 실행되도록 설계

**Next Step**
- Helm Chart로 매니페스트 템플릿화
- ArgoCD 연동으로 GitOps 배포 파이프라인 구성
- Prometheus + Grafana 등 모니터링 스택 추가