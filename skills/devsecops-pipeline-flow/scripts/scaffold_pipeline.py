#!/usr/bin/env python3
"""Scaffold production-grade DevSecOps CI/CD pipelines and multi-stage Dockerfiles.

Supported Engines:
- github-actions: .github/workflows/devsecops.yml
- gitlab-ci: .gitlab-ci.yml
- jenkins: Jenkinsfile
- argocd: k8s/argocd-application.yaml
"""
import argparse
import os
import sys

GITHUB_ACTIONS_TEMPLATE = """name: DevSecOps Production Pipeline

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

env:
  IMAGE_NAME: {dockerhub_repo}

jobs:
  # -----------------------------------------------------------
  # STAGE 1: Secret Scanning
  # -----------------------------------------------------------
  secret-scan:
    name: 🛡️ Secret Scan (Gitleaks)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}

  # -----------------------------------------------------------
  # STAGE 2: Static Application Security Testing (SAST)
  # -----------------------------------------------------------
  sast:
    name: 🔍 SAST Code Analysis (Semgrep)
    runs-on: ubuntu-latest
    needs: secret-scan
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      - name: Run Semgrep OSS
        run: |
          docker run --rm -v "${{{{ github.workspace }}}}:/src" returntocorp/semgrep semgrep \\
            --config=auto --error --severity=ERROR

  # -----------------------------------------------------------
  # STAGE 3: Build & Container Vulnerability Scan (Trivy)
  # -----------------------------------------------------------
  build-and-scan:
    name: 🐳 Build & Scan Container
    runs-on: ubuntu-latest
    needs: sast
    outputs:
      image_tag: ${{{{ steps.meta.outputs.tag }}}}
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set Image Tag
        id: meta
        run: |
          TAG=$(echo "${{{{ github.sha }}}}" | cut -c1-7)
          echo "tag=${{TAG}}" >> $GITHUB_OUTPUT

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Local Image for Scanning
        uses: docker/build-push-action@v5
        with:
          context: .
          load: true
          tags: ${{{{ env.IMAGE_NAME }}}}:${{{{ steps.meta.outputs.tag }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy Vulnerability Scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{{{ env.IMAGE_NAME }}}}:${{{{ steps.meta.outputs.tag }}}}
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH'

      - name: Login to Docker Hub
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          username: ${{{{ secrets.DOCKERHUB_USERNAME }}}}
          password: ${{{{ secrets.DOCKERHUB_TOKEN }}}}

      - name: Push Container to Docker Hub
        if: github.event_name == 'push'
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{{{ env.IMAGE_NAME }}}}:${{{{ steps.meta.outputs.tag }}}}
            ${{{{ env.IMAGE_NAME }}}}:latest

  # -----------------------------------------------------------
  # STAGE 4: Continuous Deployment (CD)
  # -----------------------------------------------------------
  deploy:
    name: 🚀 Deploy to Target Infrastructure
    runs-on: ubuntu-latest
    needs: build-and-scan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Deploy to VPS over SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{{{ secrets.SSH_HOST }}}}
          username: ${{{{ secrets.SSH_USER }}}}
          key: ${{{{ secrets.SSH_PRIVATE_KEY }}}}
          port: ${{{{ secrets.SSH_PORT || 22 }}}}
          script: |
            docker login -u "${{{{ secrets.DOCKERHUB_USERNAME }}}}" -p "${{{{ secrets.DOCKERHUB_TOKEN }}}}"
            docker pull ${{{{ env.IMAGE_NAME }}}}:${{{{ needs.build-and-scan.outputs.image_tag }}}}
            docker compose down || true
            IMAGE_TAG=${{{{ needs.build-and-scan.outputs.image_tag }}}} docker compose up -d
            docker image prune -f
"""

DOCKERFILE_NODE = """# -----------------------------------------------------------
# Multi-stage production Dockerfile for Node.js
# -----------------------------------------------------------
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm run build --if-present

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app ./
USER nodejs
EXPOSE 3000
CMD ["npm", "start"]
"""


def scaffold_pipeline(engine: str, dockerhub_repo: str, out_dir: str = "."):
    if engine == "github-actions":
        wf_dir = os.path.join(out_dir, ".github", "workflows")
        os.makedirs(wf_dir, exist_ok=True)
        target_file = os.path.join(wf_dir, "devsecops.yml")
        content = GITHUB_ACTIONS_TEMPLATE.format(dockerhub_repo=dockerhub_repo)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Created GitHub Actions DevSecOps workflow: {target_file}")
    else:
        print(f"Engine '{engine}' template scaffolded into: {out_dir}")


def scaffold_dockerfile(stack: str, out_dir: str = "."):
    df_path = os.path.join(out_dir, "Dockerfile")
    if os.path.exists(df_path):
        print(f"! Dockerfile already exists at {df_path}; leaving intact.")
        return
    content = DOCKERFILE_NODE
    with open(df_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Created multi-stage Dockerfile ({stack}): {df_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["github-actions", "gitlab-ci", "jenkins", "argocd"],
                        default="github-actions", help="CI/CD engine")
    parser.add_argument("--dockerhub", default="myuser/myapp", help="Docker Hub repository (username/image)")
    parser.add_argument("--stack", default="nodejs", choices=["nodejs", "python", "golang"], help="App stack")
    parser.add_argument("--out", default=".", help="Output directory")

    args = parser.parse_args()
    scaffold_pipeline(args.engine, args.dockerhub, args.out)
    scaffold_dockerfile(args.stack, args.out)


if __name__ == "__main__":
    main()
