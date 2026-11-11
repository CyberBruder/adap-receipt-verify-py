# adap-receipt-verify-py

🇺🇸 [Read in English](README.EN.md)

Um verificador em Python **independente** para recibos de autorização ADAP (`adap.receipt` v1), escrito a partir da especificação pública em <https://github.com/Hardalion/agent-delegated-authority>.

**Este projeto não é afiliado, endossado ou mantido por Hardalion.** Ele não importa nem copia código da implementação de referência. Ele existe para verificar se a especificação é precisa o suficiente para que uma segunda implementação, em uma linguagem diferente, alcance os mesmos resultados.

## O que ele faz

- Canonicalização RFC 8785 (JCS), incluindo formatação de números ECMAScript e ordenação de chaves em UTF-16 (`adap_receipt_verify/jcs.py`)
- Verificação de `contentHash` (seção 5 da especificação)
- Verificação de assinatura Ed25519 (seção 5, etapa 3)
- Verificação da cadeia de hashes (seção 7): sequência, `prevReceiptHash`, mesmo emissor, além de duas entradas opcionais que o verificador de referência não possui: `expected_head` (detecta final omitido) e `first_sequence` (detecta início omitido)

Um recibo verificado **sem** uma chave pública nunca é relatado como válido, pois a especificação determina que essa verificação não concluiu a etapa 3.

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

28 testes: vetores JCS, um teste diferencial contra o `JSON.stringify` do Node (a referência ECMAScript), adulteração, chave incorreta, assinatura placeholder e omissão / reordenação / início omitido / final omitido na cadeia.

Veja [FINDINGS.md](FINDINGS.md) para conferir o que a construção deste projeto revelou.

Licença: MIT
