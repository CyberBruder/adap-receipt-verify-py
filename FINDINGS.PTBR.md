# adap-receipt-verify-py

<div align="right">
  <a href="README.md">🇺🇸 Read in English</a>
</div>

<br>

Um verificador em Python **independente** para recibos de autorização ADAP
(`adap.receipt` v1), escrito a partir da especificação pública em
<https://github.com/Hardalion/agent-delegated-authority>.

**Este projeto não é afiliado, endossado ou mantido pela Hardalion.**
Ele não importa nem copia código da implementação de referência. Ele existe para
verificar se a especificação é precisa o suficiente para que uma segunda implementação, em uma
linguagem diferente, alcance os mesmos resultados.

Especificação: ADAP, © Hardalion, Apache-2.0. Este repositório não contém código daquele projeto.

## O que ele faz

- Canonização RFC 8785 (JCS), incluindo formatação de números ECMAScript e
  ordenação de chaves UTF-16 (`adap_receipt_verify/jcs.py`)
- Verificação de `contentHash` (seção 5 da especificação)
- Verificação de assinatura Ed25519 (seção 5, passo 3)
- Verificação da cadeia de hashes (seção 7): sequência, `prevReceiptHash`, mesmo emissor, além de duas
  entradas opcionais que o verificador de referência não possui: `expected_head` (detecta a
  perda do final/tail) e `first_sequence` (detecta a perda do início/head)

Um recibo verificado **sem** uma chave pública nunca é reportado como válido, pois a
especificação diz que a verificação não concluiu o passo 3.

## Uso

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

## Testes

28 testes: vetores JCS, um teste diferencial contra o `JSON.stringify` do Node (a
referência ECMAScript), adulteração, chave incorreta, assinatura temporária (placeholder) e
omissão / reordenação / perda do início (dropped head) / perda do final (dropped tail) da cadeia.

Consulte [FINDINGS.md](FINDINGS.md) para ver o que a construção deste projeto revelou.

Licença: MIT

---

## Como Rodar o Projeto Localmente

Se você quiser clonar este repositório e rodar o projeto na sua máquina:

1. Certifique-se de ter o Docker instalado no seu sistema.

2. Na raiz do projeto, construa a imagem Docker localmente:

   ```bash
   docker build -t meu-app-java .
   ```

3. Inicie o container mapeando as portas:

   ```bash
   docker run -p 8080:8080 meu-app-java
   ```

4. Abra o navegador e acesse: http://localhost:8080

## O Pipeline de CI/CD (GitHub Actions)

A esteira de automação foi configurada para eliminar qualquer trabalho manual de deploy. O fluxo funciona da seguinte forma:

1. **Gatilho:** O desenvolvedor faz um `git push` na branch principal (`main`).
2. **Ambiente:** O GitHub Actions inicializa uma máquina virtual isolada com `ubuntu-latest`.
3. **Autenticação:** A esteira faz login no Docker Hub usando credenciais seguras (Repository Secrets).
4. **Build & Push:** O Dockerfile é lido, o código Java é compilado dentro do container e a imagem final é enviada para o Docker Hub com duas tags:

   * `latest` (para a versão mais recente).
   * Uma tag com a SHA (identificador único) daquele commit específico para histórico.

## Executando a partir da Nuvem (Portabilidade)

Graças ao Docker Hub, você não precisa clonar este código para rodar a aplicação. Em qualquer servidor ou computador do mundo que tenha o Docker instalado, basta executar:

```bash
docker run -d -p 8080:8080 --name meu-servidor-java JustBruder/my-docker:latest
```

- Ver logs do app:

  ```bash
  docker logs meu-servidor-java
  ```

- Parar o app:

  ```bash
  docker stop meu-servidor-java
  ```

---

### 💻 Contate-me / Let's Connect

<p align="center">
  <a href="https://www.linkedin.com/in/ingrid-bruder" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-C71585?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="mailto:ibruder83@gmail.com">
    <img src="https://img.shields.io/badge/Email-C71585?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
  <a href="https://www.instagram.com/Cyber.Bruder" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-C71585?style=for-the-badge&logo=instagram&logoColor=white" />
  </a>
  <a href="https://www.tiktok.com/@Cyber.Bruder" target="_blank">
    <img src="https://img.shields.io/badge/TikTok-C71585?style=for-the-badge&logo=tiktok&logoColor=white" />
  </a>
</p>

<div align="center">
  <sub>Desenvolvido por Bruder ✨</sub>
</div>
<div align="center">
  <sub>🌷🐱 Código limpo e MEOW </sub>
</div>
