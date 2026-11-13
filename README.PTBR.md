<div align="right">
  <a href="README.md">🇺🇸 Read in English</a>
</div>

# adap-receipt-verify-py

Um verificador em Python **independente** para recibos de autorização ADAP
(`adap.receipt` v1), escrito a partir da especificação pública em
<https://github.com/Hardalion/agent-delegated-authority>.

**Este projeto não é afiliado, endossado ou mantido pela Hardalion.**
Ele não importa nem copia código da implementação de referência. Ele existe para
verificar se a especificação é precisa o suficiente para que uma segunda
implementação, em uma linguagem diferente, alcance os mesmos resultados.

Especificação: ADAP, © Hardalion, Apache-2.0. Este repositório não contém código desse projeto.

## O que ele faz

- Canonicalização RFC 8785 (JCS), incluindo formatação de números ECMAScript e
  ordenação de chaves em UTF-16 (`adap_receipt_verify/jcs.py`)
- Verificação de `contentHash` (seção 5 da especificação)
- Verificação de assinatura Ed25519 (seção 5, etapa 3)
- Verificação da cadeia de hashes (seção 7): sequência, `prevReceiptHash`, mesmo
  emissor, além de duas entradas opcionais que o verificador de referência não
  possui: `expected_head` (detecta final omitido) e `first_sequence` (detecta
  início omitido)

Um recibo verificado **sem** uma chave pública nunca é relatado como válido, pois
a especificação determina que essa verificação não concluiu a etapa 3.

## Instalação e uso

Requer Python 3.10 ou superior.

```bash
git clone https://github.com/cyberbruder/adap-receipt-verify-py.git
cd adap-receipt-verify-py
pip install cryptography pytest
python -m pytest -q
```

Verificar o recibo de demonstração (assinado com uma chave de demonstração
descartável, gerado por `examples/make_example.py`):

```bash
python -m adap_receipt_verify examples/receipt.json --public-key MCowBQYDK2VwAyEAO3ukXVBh31tLC1HPgzy9MHlKtBOde9CTrkHYR55O3-8
```

Como biblioteca:

```python
from adap_receipt_verify import verify_receipt, verify_chain

result = verify_receipt(receipt, public_key_spki_b64url)
result.valid, result.errors

chain = verify_chain(receipts, public_key_spki_b64url,
                     expected_head=known_head_hash, first_sequence=0)
chain.valid, chain.errors
```

## Estrutura do projeto

```
adap_receipt_verify/
  jcs.py        canonicalização RFC 8785
  verify.py     contentHash, assinatura Ed25519, cadeia de hashes
  __main__.py   ponto de entrada de linha de comando
tests/          vetores JCS, adulteração, testes de cadeia
examples/       recibo de demonstração e o script que o gera
```

## Testes

28 testes: vetores JCS, um teste diferencial contra o `JSON.stringify` do Node (a
referência ECMAScript), adulteração, chave incorreta, assinatura placeholder e
omissão / reordenação / início omitido / final omitido na cadeia.

## Limites

Apenas as verificações criptográficas estão implementadas. A validação de
estrutura (tipos de campos, invariantes semânticas) não está. Testado com um
recibo de demonstração e com recibos gerados pelos próprios testes, não com um
conjunto vindo do emissor de referência.

Veja o [FINDINGS.PTBR.md](FINDINGS.PTBR.md) para saber o que a construção deste
projeto revelou.

Licença: MIT

---

### 💻 Vamos nos conectar

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
  <sub>🌷🐱 Clean code and MEOW</sub>
</div>