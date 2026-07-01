# Prometheus와 Grafana로 Ubuntu 서버 모니터링 환경 구성하기

![image.png](Prometheus%EC%99%80%20Grafana%EB%A1%9C%20Ubuntu%20%EC%84%9C%EB%B2%84%20%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81%20%ED%99%98%EA%B2%BD%20%EA%B5%AC%EC%84%B1%ED%95%98%EA%B8%B0/image.png)

# 개요

사내에서 여러 개발용 서버를 운영하다 보면 디스크 용량 부족, CPU 사용률 급증, 메모리 사용량 증가 같은 문제를 자주 만나게 됩니다. 이런 상황이 발생하면 서비스가 일시적으로 멈칫하거나, 심한 경우 실제 장애로 이어지기도 합니다.

문제가 생길 때마다 직접 서버에 터미널로 접속해서 CPU, 메모리, 디스크 상태를 확인하는 방식은 번거롭고 대응도 늦어질 수 있습니다. 그래서 이번 기회에 Prometheus와 Grafana를 사용해 서버 모니터링 인프라를 구성하기로 했습니다.

이번 구성의 목표는 다음과 같습니다.

- 여러 Ubuntu 서버의 CPU, Memory, Disk, Network 상태를 중앙에서 수집합니다.
- Grafana 대시보드를 통해 서버 상태를 한눈에 확인합니다.
- 특정 threshold를 넘으면 Slack 또는 MS Teams로 알림을 보냅니다.
- 처음에는 구성을 단순하게 가져가기 위해 node_exporter 중심으로 구축합니다.

## 전체적인 구조

전체적인 구조는 다음과 같다.

```
[Ubuntu 서버들]
  └─ node_exporter : CPU / Memory / Disk / Network / Filesystem 메트릭 노출
  └─ cAdvisor      : Docker 컨테이너 단위 CPU / Memory / Disk / Network 메트릭, 선택

        ↓ scrape

[중앙 모니터링 서버]
  └─ Prometheus : 메트릭 수집/저장
  └─ Grafana    : 대시보드 + Alert Rule + Slack / MS Teams 알림
```

처음부터 모든 구성을 한 번에 넣기보다는, 우선 cAdvisor는 제외하고 node_exporter 기반으로 먼저 구축합니다. 중앙 모니터링 서버 한 대에 Prometheus와 Grafana를 구성하고, 모니터링 대상 서버에는 node_exporter를 설치해 메트릭을 노출하는 방식입니다.

추후에는 더 자세하게 Docker 컨테이너 단위의 메트릭이 필요해지면 cAdvisor를 추가하면 됩니다.

## 중앙 모니터링 서버 구성

먼저 중앙 모니터링 서버에서 사용할 디렉터리를 생성합니다. 이 서버에서는 Prometheus, Grafana를 구성할 것입니다. 

```
mkdir -p ~/monitoring/prometheus
mkdir -p ~/monitoring/grafana/provisioning/datasources
cd ~/monitoring
```

다음과 같이 docker-compose.yml을 설정해줍니다. 

Prometheus에는 retention 설정을 꼭 넣어주는 것이 좋습니다. retention을 설정하지 않으면 시간이 지나면서 Prometheus 데이터가 계속 쌓이고, 결국 모니터링 서버 자체의 디스크 장애로 이어질 수 있습니다.

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.retention.time=30d
      - --storage.tsdb.retention.size=20GB
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/targets:/etc/prometheus/targets:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: {admin-password}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  grafana-data:
```

## Grafana datasource 자동 등록

Grafana에서 Prometheus datasource를 매번 UI로 등록하지 않도록 provisioning 설정을 추가합니다.

```yaml
vi ./grafana/provisioning/datasources/prometheus.yml
```

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

이렇게 설정하면 Grafana 컨테이너가 실행될 때 Prometheus datasource가 자동으로 등록됩니다.

## Prometheus scrape 설정

이제 Prometheus가 어떤 서버에서 메트릭을 수집할지 설정해야 합니다.

Prometheus target을 설정하는 방식은 크게 `static_configs`와 `file_sd_configs`가 있는데 추후 확장성 및 관리 측면에서 봤을 때 target 목록을 별도 파일로 관리할 수 있는 `file_sd_configs` 방식을 사용합니다.

서버가 늘어나거나 줄어들 때 Prometheus 설정 파일 전체를 수정하는 대신, target 파일만 수정하면 되기 때문에 운영 측면에서 더 깔끔합니다.

```yaml
$ vi prometheus/prometheus.yml 
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "ubuntu-node"
    file_sd_configs:
      - files:
          - /etc/prometheus/targets/ubuntu-nodes.yml
        refresh_interval: 30s

  - job_name: "cadvisor"
    file_sd_configs:
      - files:
          - /etc/prometheus/targets/cadvisor.yml
        refresh_interval: 30s
```

위 설정에서는 `ubuntu-node`와 `cadvisor` job을 정의했습니다. 실제로 cAdvisor를 아직 사용하지 않더라도, 추후 확장을 고려해 job만 미리 잡아둘 수 있습니다.

`file_sd_configs` 방식의 장점은 target 파일이 변경되었을 때 Prometheus를 매번 재기동하지 않아도 된다는 점입니다. Prometheus는 `refresh_interval`에 따라 target 파일을 다시 읽고 목록을 갱신합니다.

```yaml
$ vi prometheus/targets/ubuntu-nodes.yml 
- targets:
    - "192.168.xxx.xxx:9100"
  labels:
    role: "infra"
    env: "local"

- targets:
    - "192.168.xxx.xxx:9100"
  labels:
    role: "local-test"
    env: "local"

- targets:
    - "192.168.xxx.xxx:9100"
    ...
  labels:
    role: "k8s"
    env: "local"
```

target group마다 `role`, `env` 같은 label을 붙여두면 Grafana 대시보드나 Alert Rule에서 필터링하기가 쉬워집니다.

## cAdvisor target group 참고

Docker 컨테이너 단위 메트릭까지 보고 싶다면 cAdvisor target 파일도 추가할 수 있습니다.

- 이번 구성에서는 우선 node_exporter를 중심으로 진행하고, cAdvisor는 참고용으로만 남겨둡니다.
    
    ```yaml
    vi prometheus/targets/cadvisor.yml
    ```
    
    ```yaml
    - targets:
        - "192.168.0.13:8080"
      labels:
        hostname: "docker-01"
        role: "docker"
        env: "local"
    ```
    

## Prometheus와 Grafana 실행

설정 파일 작성이 끝났다면 Docker Compose로 실행합니다.

```yaml
docker compose up -d
```

정상적으로 서버가 구동됐는지 확인합니다. 

- Prometheus: `http://<MONITORING_SERVER_IP>:9090`
- Grafana: `http://<MONITORING_SERVER_IP>:3000`

## 각 서버에 node_exporter 설치 (cAdvisor 설치는 메모만)

이제 메트릭을 수집하고 싶은 각 Ubuntu 서버에 node_exporter를 설치합니다.

Ubuntu에서는 apt 패키지를 통해 간단하게 설치할 수 있습니다.

```yaml
sudo apt update
sudo apt install -y prometheus-node-exporter

sudo systemctl enable --now prometheus-node-exporter
sudo systemctl status prometheus-node-exporter
```

정상적으로 실행되었다면, 로컬에서 metrics endpoint를 확인합니다.

```yaml
curl http://localhost:9100/metrics | head
```

만약 아래와 같이 나온다면, 정상적으로 완료된 것이다. 마지막에 보이는 `curl: (23) Failure writing output to destination` 에러는 `head` 명령으로 인해 발생한 메시지이므로 오류가 발생한게 아니기 때문에 무시해도 됩니다. 이 앞부분만 출력하고 종료하면서, curl이 나머지 데이터를 쓰지 못해 발생하는 메시지입니다.

```yaml
curl http://localhost:9100/metrics | head
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0# HELP apt_autoremove_pending Apt package pending autoremove.
# TYPE apt_autoremove_pending gauge
apt_autoremove_pending 0
# HELP apt_upgrades_pending Apt package pending updates by origin.
# TYPE apt_upgrades_pending gauge
apt_upgrades_pending{arch="all",origin="Ubuntu:22.04/jammy-updates"} 16
apt_upgrades_pending{arch="all",origin="Ubuntu:22.04/jammy-updates,Ubuntu:22.04/jammy-security"} 34
apt_upgrades_pending{arch="amd64",origin="DockerCE:jammy"} 6
apt_upgrades_pending{arch="amd64",origin="ProprietaryGPUDrivers:22.04/jammy"} 1
apt_upgrades_pending{arch="amd64",origin="Ubuntu:22.04/jammy-updates"} 53
100 16190    0 16190    0     0   123k      0 --:--:-- --:--:-- --:--:--  123k
curl: (23) Failure writing output to destination
```

Prometheus 서버에서 각 Ubuntu 서버의 `9100/tcp`에 접근 가능해야 하기 때문에 만약 ufw 방화벽을 사용 중이면 각 Ubuntu 서버에서 허용을 해줘야 합니다.

```
sudo ufw allow from <PROMETHEUS_SERVER_IP> to any port 9100 proto tcp
```

## cAdvisor 구성 참고

Docker 컨테이너별 CPU, 메모리, 네트워크, filesystem 사용량까지 보고 싶다면 각 Docker 호스트에 cAdvisor를 실행하면 됩니다.

cAdvisor는 컨테이너 및 하드웨어 통계를 Prometheus metrics 형식으로 `/metrics` endpoint에 노출합니다.

- cAdvisor 구성은 참고만
    
    Docker 컨테이너별 CPU, 메모리, 네트워크, filesystem 사용량까지 보려면 각 Docker 호스트에 cAdvisor를 실행하여 cAdvisor는 컨테이너 및 하드웨어 통계를 Prometheus metrics로 `/metrics`에 노출합니다
    
    ```yaml
    docker run -d \
      --name=cadvisor \
      --restart=unless-stopped \
      -p 8080:8080 \
      --volume=/:/rootfs:ro \
      --volume=/var/run:/var/run:ro \
      --volume=/sys:/sys:ro \
      --volume=/var/lib/docker/:/var/lib/docker:ro \
      --privileged \
      gcr.io/cadvisor/cadvisor:latest
    ```
    
    마찬가지로 Prometheus 서버에서 cAdvisor 포트에 접근할 수 있어야 합니다.
    
    ```yaml
    sudo ufw allow from <PROMETHEUS_SERVER_IP> to any port 8080 proto tcp
    ```
    

## Grafana 대시보드 구성

Grafana에 접속한 뒤 대시보드를 import합니다.

```
Dashboards → New → Import dashboard
```

찾아보니 node_exporter 기반 대시보드로는 다음 Dashboard ID를 많이 사용합니다.

```
Dashboard ID: 1860 또는 12486
```

![image.png](Prometheus%EC%99%80%20Grafana%EB%A1%9C%20Ubuntu%20%EC%84%9C%EB%B2%84%20%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81%20%ED%99%98%EA%B2%BD%20%EA%B5%AC%EC%84%B1%ED%95%98%EA%B8%B0/image%201.png)

두 대시보드를 비교해본 결과, Host가 IP 기준으로 표시되는 점과 UI 구성이 더 마음에 들어 `12486`을 사용했습니다.

# Alert Rule 구성

사실 이번 포스팅의 핵심은 Alert 부분이다. 모니터링 UI를 구축했다고 해도 사람이 이걸 계속 볼 수는 없으니까 특정 threshold가 넘어서면 관리자에게 알림을 보내 재빠르게 대응할 수 있는 장점이 있다.

이번에 구성할 알람의 전체 구성은 다음과 같습니다.

```yaml
Prometheus
  └─ node_exporter 메트릭 수집

Grafana v13.1.0
  ├─ Contact point: MS Teams (또는 Slack)
  ├─ Notification policy: severity, team, service label 기준 라우팅
  └─ Alert rules:
       - HostDown
       - CPUHigh
       - MemoryHigh
       - DiskUsageHigh
       - InodeUsageHigh
       - DiskWillFillSoon
       ...
```

Grafana에서 알림을 보내는 실제 목적지는 **Contact point**입니다. Slack, MS Teams, Webhook 같은 발송 채널을 Contact point로 정의합니다.

반면 **Notification policy**는 어떤 alert를 어떤 Contact point로 보낼지 결정하는 라우팅 규칙입니다. 보통 `severity`, `team`, `service` 같은 label을 기준으로 알림을 분기합니다.

운영에서는 Alert Rule에 Contact point를 직접 붙이는 방식보다, Alert Rule은 조건만 담당하고 Notification policy가 라우팅을 담당하도록 나누는 편이 좋습니다.

## MS Teams workflow 구성

Grafana에서 MS Teams로 알림을 보내려면 먼저 Teams 쪽에서 webhook request를 받을 수 있는 Workflow를 만들어야 합니다.

```
MS Teams → 원하는 Channel → Workflow 생성
→ Webhook request 수신 Workflow 생성
→ Webhook URL 복사
```

![823A08BD-E357-4946-8B65-F0EF63F8D997.png](Prometheus%EC%99%80%20Grafana%EB%A1%9C%20Ubuntu%20%EC%84%9C%EB%B2%84%20%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81%20%ED%99%98%EA%B2%BD%20%EA%B5%AC%EC%84%B1%ED%95%98%EA%B8%B0/823A08BD-E357-4946-8B65-F0EF63F8D997.png)

Teams Workflow에서 발급받은 Webhook URL은 이후 Grafana Contact point 설정에 사용합니다.

MS Teams Webhook 구성에 대한 자세한 설명은 이 글에서는 생략합니다.

## MS Teams Contact point 만들기

Teams는 먼저 Teams 쪽에서 Webhook을 받는 Workflow를 만들어 URL을 받아야 합니다. Grafana 공식 문서 기준으로 Teams에서는 “Post to a channel when a webhook request is received” 템플릿을 사용할 수 있고, Grafana에서는 Microsoft Teams integration에 해당 Webhook URL을 넣습니다.

Grafana UI:

```
Alerts & IRM
→ Alerting
→ Notification configuration
→ Contact points
→ + Add contact point
```

입력값:

| 항목 | 값 |
| --- | --- |
| Name | `teams-infra` |
| Integration | `Microsoft Teams` |
| URL | Teams Workflow Webhook URL |

## Notification policy 만들기

Alert Rule마다 직접 Contact point를 지정할 수도 있지만, 운영 환경에서는 Notification policy를 사용하는 편이 낫습니다.

역할을 분리하면 다음과 같이 관리할 수 있습니다.

```
Alert rule은 조건만 담당
Notification policy는 라우팅만 담당
Contact point는 발송지만 담당
```

Grafana UI에서 다음 메뉴로 이동합니다.

```
Alerts & IRM
→ Alerting
→ Notification configuration
→ Notification policies
```

## Default policy 설정

먼저 기본 정책을 설정합니다.

```
Default policy → ... → Edit
```

추천 설정값은 다음과 같습니다.

| 항목 | 값 |
| --- | --- |
| Default contact point | `teams-infra` |
| Group by | `alertname`, `hostname`, `severity` |
| Group wait | `30s` |
| Group interval | `5m` |
| Repeat interval | `4h` |

Notification policy는 비슷한 alert를 grouping하고, `group wait`, `group interval`, `repeat interval` 설정을 통해 알림 주기를 제어합니다.

## Alert rule 공통 설정

이제 실제 Alert Rule을 만듭니다.

Grafana UI에서 다음 메뉴로 이동합니다.

```
Alerts & IRM
→ Alerting
→ Alert rules
→ + New alert rule
```

Grafana-managed alert rule 생성 화면에서는 보통 다음 순서로 설정합니다.

- Rule name
- Data source
- Query
- Condition
- Evaluation behavior
- Labels
- Annotations
- Notification

## Alert rule 공통 설정값

각 Alert Rule마다 공통으로 사용할 값은 거의 동일합니다.

Folder는 다음과 같이 설정합니다.

```
Folder: Infra Alerts
```

Folder가 없다면 새로 생성합니다.

Evaluation group은 다음과 같이 설정합니다.

```
Evaluation group: infra-1m
Evaluation interval: 1m
```

Grafana에서 같은 evaluation group 안에 있는 rule은 같은 interval로 평가됩니다.

운영 초기에는 No data / Error handling을 다음처럼 설정하는 것을 권장합니다.

| 항목 | 추천값 |
| --- | --- |
| No data state | `Alerting` |
| Error state | `Alerting` |
| Keep firing for | `5m` |

node_exporter, Prometheus, 네트워크 쪽에 문제가 생기면 “데이터 없음” 자체가 장애 신호가 될 수 있습니다. 따라서 초기에는 No data 상태도 Alerting으로 처리하는 편이 장애 감지에 유리합니다.

다만 알림이 너무 자주 발생한다면 다음처럼 완화할 수 있습니다.

| 항목 | 완화값 |
| --- | --- |
| No data state | `Keep last state` |
| Error state | `Alerting` |

## Host Down 알림

이 알림은 서버 또는 node_exporter가 응답하지 않을 때 발생합니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `HostDown` |
| Datasource | `Prometheus` |
| Query A | `up{job="ubuntu-node"} == 0` |
| Condition | `WHEN QUERY IS ABOVE 0` |
| Labels | `severity=critical`, `team=infra`, `service=node`, `category=availability` |
| Evaluation group | `infra-1m` |
| Pending period | `1m` |
| Keep firing for | `5m` |
| Summary | 서버 또는 node_exporter가 응답하지 않습니다. |
| Description | `{{ $labels.hostname }} / {{ $labels.instance }} 의 up 메트릭이 0입니다.` |

## CPU 사용률 80% 이상 알림

CPU는 순간 spike가 자주 발생하기 때문에 단순 현재값보다는 `5m rate`를 기준으로 보는 것이 좋습니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `CPUHighWarning` |
| Datasource | `Prometheus` |
| Query A | `100 * (1 - avg by(instance, hostname) (rate(node_cpu_seconds_total{job="ubuntu-node", mode="idle"}[5m])))` |
| Condition | `WHEN QUERY OF A IS ABOVE 80` |
| Labels | `severity=warning`, `team=infra`, `service=node`, `category=cpu` |
| Evaluation group | `infra-1m` |
| Pending period | `10m` |
| Keep firing for | `5m` |
| Summary | CPU 사용률이 80%를 초과했습니다. |
| Description | `{{ $labels.hostname }} / {{ $labels.instance }} CPU 사용률이 80% 초과` |

CPU Critical 알림은 위 Rule을 복제해서 값만 변경합니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `CPUHighCritical` |
| Threshold | `IS ABOVE 90` |
| Pending period | `10m` |
| severity | `critical` |

## Memory 사용률 85% 이상 알림

Linux에서는 단순 used 기준보다 `MemAvailable` 기준으로 메모리 사용률을 계산하는 편이 더 적합합니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `MemoryHighWarning` |
| Datasource | `Prometheus` |
| Query A | `100 * (1 - (node_memory_MemAvailable_bytes{job="ubuntu-node"} / node_memory_MemTotal_bytes{job="ubuntu-node"}))` |
| Condition | `WHEN QUERY OF A IS ABOVE 85` |
| Labels | `severity=warning`, `team=infra`, `service=node`, `category=memory` |
| Evaluation group | `infra-1m` |
| Pending period | `10m` |
| Keep firing for | `5m` |
| Summary | 메모리 사용률이 85%를 초과했습니다. |
| Description | `{{ $labels.hostname }} / {{ $labels.instance }} 메모리 사용률 85% 초과` |

Memory Critical 알림은 위 Rule을 복제해서 적절히 값만 변경합니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `MemoryHighCritical` |
| Threshold | `IS ABOVE 95` |
| Pending period | `5m` |
| severity | `critical` |

## Disk 사용률 80% 이상 알림

Docker 서버에서는 `overlay`, `tmpfs`, `snap` 같은 mount가 많기 때문에 filesystem 필터링이 중요합니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `DiskUsageHighWarning` |
| Datasource | `Prometheus` |
| Query A | `100 * (1 - (node_filesystem_avail_bytes{job="ubuntu-node", fstype!~"tmpfs |
| Condition | `WHEN QUERY OF A IS ABOVE 80` |
| Labels | `severity=warning`, `team=infra`, `service=node`, `category=disk` |
| Evaluation group | `infra-1m` |
| Pending period | `10m` |
| Keep firing for | `10m` |
| Summary | 디스크 사용률이 80%를 초과했습니다. |
| Description | `{{ $labels.hostname }} / {{ $labels.instance }} 디스크 사용률 80% 초과` |

Disk Critical 알림은 위 Rule을 복제해서 값만 변경합니다.

| 항목 | 값 |
| --- | --- |
| Rule name | `DiskUsageHighCritical` |
| Threshold | `IS ABOVE 90` |
| Pending period | `5m` |
| severity | `critical` |

## 알림 테스트 방법

처음에는 실제 장애를 기다리지 말고, threshold를 임시로 낮춰 강제로 알림을 발생시키는 방식으로 테스트하는 것이 좋습니다.

예를 들어 CPU warning rule의 threshold를 임시로 낮춥니다.

```
CPUHighWarning threshold: 1
Pending period: 0m 또는 1m
```

저장 후 설정해둔 Teams로 알림이 정상적으로 오는지 확인합니다.

![BEED0516-FBC9-4761-9A7B-B2676B894E0B.png](Prometheus%EC%99%80%20Grafana%EB%A1%9C%20Ubuntu%20%EC%84%9C%EB%B2%84%20%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81%20%ED%99%98%EA%B2%BD%20%EA%B5%AC%EC%84%B1%ED%95%98%EA%B8%B0/BEED0516-FBC9-4761-9A7B-B2676B894E0B.png)

테스트가 끝나면 다시 원래 값으로 되돌립니다.

```
Threshold: 80
Pending period: 10m
```

## 마무리

![image.png](Prometheus%EC%99%80%20Grafana%EB%A1%9C%20Ubuntu%20%EC%84%9C%EB%B2%84%20%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81%20%ED%99%98%EA%B2%BD%20%EA%B5%AC%EC%84%B1%ED%95%98%EA%B8%B0/image%202.png)

그동안 구성해야지만 반복했던 귀차니즘을 이겨내고 이번 구성으로 여러 Ubuntu 서버의 기본 리소스 상태를 Prometheus와 Grafana를 통해 한곳에서 확인할 수 있게 되어 저 또는 팀원들의 불편함까지 해소할 수 있다는 사실에 정말 뿌듯합니다. 다음에는 서비스하는 애플리케이션까지 추가로 모니터링을 구성하여 장애로 이어지기전 사전에 탐지하여 방지할 수 있는 인프라를 구축하고 싶습니다.