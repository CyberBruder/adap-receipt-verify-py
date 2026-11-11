# adap-receipt-verify-py

<div align="right">
  <a href="README.PTBR.md">🇧🇷 Leia em Português</a>
</div>

<br>

An **independent** Python verifier for ADAP authorization receipts
(`adap.receipt` v1), written from the public spec at
<https://github.com/Hardalion/agent-delegated-authority>.

**This project is not affiliated with, endorsed by, or maintained by Hardalion.**
It does not import or copy code from the reference implementation. It exists to
check that the spec is precise enough for a second implementation, in a different
language, to reach the same results.

Spec: ADAP, © Hardalion, Apache-2.0. This repository contains no code from that project.

## What it does

- RFC 8785 (JCS) canonicalization, including ECMAScript number formatting and
  UTF-16 key ordering (`adap_receipt_verify/jcs.py`)
- `contentHash` check (spec section 5)
- Ed25519 signature check (section 5, step 3)
- Hash-chain check (section 7): sequence, `prevReceiptHash`, same issuer, plus two
  optional inputs the reference verifier does not have: `expected_head` (detects a
  dropped tail) and `first_sequence` (detects a dropped head)

A receipt checked **without** a public key is never reported as valid, because the
spec says that check has not completed step 3.

## Usage

```bash
pip install cryptography pytest
python -m adap_receipt_verify examples/receipt.json --public-key MCowBQYDK2VwAyEAO3ukXVBh31tLC1HPgzy9MHlKtBOde9CTrkHYR55O3-8
python -m pytest -q
```

```python
from adap_receipt_verify import verify_receipt, verify_chain
result = verify_receipt(receipt, public_key_spki_b64url)
result.valid, result.errors
```

## Tests

28 tests: JCS vectors, a differential test against Node's `JSON.stringify` (the
ECMAScript reference), tampering, wrong key, placeholder signature, and chain
omission / reordering / dropped head / dropped tail.

See [FINDINGS.md](FINDINGS.md) for what building this turned up.

License: MIT

---

## How to Run the Project Locally

If you want to clone this repository and run the project on your machine:

1. Make sure Docker is installed on your system.

2. From the project root, build the Docker image locally:

   ```bash
   docker build -t meu-app-java .
   ```

3. Start the container, mapping the ports:

   ```bash
   docker run -p 8080:8080 meu-app-java
   ```

4. Open your browser and go to: http://localhost:8080

## The CI/CD Pipeline (GitHub Actions)

The automation pipeline was set up to eliminate any manual deployment work. It works like this:

1. **Trigger:** The developer runs `git push` on the main branch (`main`).
2. **Environment:** GitHub Actions starts an isolated virtual machine with `ubuntu-latest`.
3. **Authentication:** The pipeline logs in to Docker Hub using secure credentials (Repository Secrets).
4. **Build & Push:** The Dockerfile is read, the Java code is compiled inside the container, and the final image is pushed to Docker Hub with two tags:

   * `latest` (for the most recent version).
   * A tag with the SHA (unique identifier) of that specific commit, for history.

## Running from the Cloud (Portability)

Thanks to Docker Hub, you don't need to clone this code to run the application. On any server or computer in the world that has Docker installed, just run:

```bash
docker run -d -p 8080:8080 --name meu-servidor-java JustBruder/my-docker:latest
```

* View the app logs:

  ```bash
  docker logs meu-servidor-java
  ```

* Stop the app:

  ```bash
  docker stop meu-servidor-java
  ```

---

### 💻 Let's Connect

<p align="center">
  <a href="https://www.linkedin.com/in/ingrid-bruder" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-C71585?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="mailto:ibruder83@gmail.com">
    <img src="https://img.shields.io/badge/Email-C71585?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
  <a href="https://www.instagram.com/JustBruder" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-C71585?style=for-the-badge&logo=instagram&logoColor=white" />
  </a>
  <a href="https://www.tiktok.com/@JustBruder" target="_blank">
    <img src="https://img.shields.io/badge/TikTok-C71585?style=for-the-badge&logo=tiktok&logoColor=white" />
  </a>
</p>

<div align="center">
  <sub>Developed by JustBruder ✨</sub>
</div>
<div align="center">
  <sub>🌷🐱 Clean code and MEOW </sub>
</div>
