import logging
import os
import subprocess
from datetime import datetime

import requests
import yaml
from minio import Minio
from minio.error import S3Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ScanAndNotify:

    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.minio_endpoint = os.getenv('MINIO_ENDPOINT')
        self.minio_access_key = os.getenv('MINIO_ACCESS_KEY')
        self.minio_secret_key = os.getenv('MINIO_SECRET_KEY')
        self.minio_bucket = os.getenv('MINIO_BUCKET')
        self.report_name = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        self.minio_client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False
        )

    @staticmethod
    def get_server_list():
        try:
            with open('config/servers.yaml', 'r') as f:
                servers = yaml.safe_load(f)
            return servers.get('servers', [])
        except IOError:
            raise IOError("Failed to read servers.yaml file")

    def send_notification(self, message: str) -> None:
        try:
            payload = {"text": message}
            requests.post(self.slack_webhook_url, json=payload)
            logging.info(f"Notification sent: {message}")
        except Exception as e:
            logging.error(f"Failed to send notification: {str(e)}")

    def upload_to_minio(self, report_path: str) -> None:
        bucket_name = self.minio_bucket
        report_name = os.path.basename(report_path)

        try:
            self.minio_client.fput_object(bucket_name, report_name, report_path)
            logging.info(f"Report uploaded successfully: {report_name}")
        except S3Error as e:
            logging.error(f"Failed to upload report: {str(e)}")

    def run_scan(self, server_ip: str) -> None:
        report_path = f"/tmp/{server_ip}_{self.report_name}"
        command = [
            "docker", "run", "--rm",
            "-v", "/tmp:/tmp",
            "omeritzhaki/tsunami-scanner:latest",
            "--ip-v4-target", server_ip,
            "--scan-results-local-output-format", "JSON",
            "--scan-results-local-output-filename", report_path
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            logging.info(f"Docker run command output: {result.stdout}")
            logging.info(f"Docker run command error (if any): {result.stderr}")
            if os.path.exists(report_path):
                logging.info(f"Scan report created: {report_path}")
                self.upload_to_minio(report_path)
                self.send_notification(f"Scan result for {server_ip}:\n{report_path}")
            else:
                logging.error(f"Scan report not found: {report_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to run scan: {str(e)}")


if __name__ == "__main__":
    scan_and_notify = ScanAndNotify()
    servers = scan_and_notify.get_server_list()
    for server in servers:
        logging.info(f"Scanning server: {server}")
        scan_and_notify.run_scan(server)
        logging.info(f"Finished scanning server: {server}")
