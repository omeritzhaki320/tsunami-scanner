# Tsunami Scanner Deployment

## Overview
This repository contains the necessary files to deploy a Tsunami network scanner in a Kubernetes cluster to identify vulnerabilities on a list of servers, notify via Slack, and upload reports to Minio.

## Prerequisites
- Kubernetes cluster
- Docker
- Slack webhook URL
- Minio (local or cloud)
- Helm

## Deployment Instructions

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/omeritzhaki320/tsunami-scanner.git
   cd tsunami-scanner
   ```

2. **Run Minio Locally::**
   ```sh
    docker run -p 9000:9000 -p 9001:9001 --name minio \
      -e MINIO_ROOT_USER=minioadmin \
      -e MINIO_ROOT_PASSWORD=minioadmin \
      minio/minio server /data --console-address ":9001"
   ```

3. **Create a Bucket in Minio:**
Access the Minio web interface at http://localhost:9001, log in with the credentials minioadmin:minioadmin, and create a bucket named tsunami-reports.

4. **Update Values File:**
Update the values.yaml file in the Helm chart directory with your specific configuration values.

5. **Package and Install the Helm Chart:**
   ```sh
   helm package .
   helm install tsunami-scan ./tsunami-scan-0.1.0.tgz
   ```
   
## Conclusion
This solution periodically scans the specified servers for vulnerabilities using the Tsunami network scanner, sends notifications via Slack, and uploads scan reports to Minio.