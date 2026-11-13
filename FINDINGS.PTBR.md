<div align="right">
  <a href="FINDINGS.md">🇺🇸 Read in English</a>
</div>

# Achados de uma segunda implementação

Notas de quem implementou um verificador de recibos ADAP em Python a partir da
especificação pública. Cada item diz como reproduzir. Os itens 1, 2 e 4 foram
reportados ao projeto original.

## 1. Chaves com aparência de inteiro eram ordenadas pela ordem de inserção (reportado, correção pendente)

Na referência em TypeScript, `canonicalReceiptJson` ordenava as chaves e depois as
copiava para um objeto JavaScript comum. O JavaScript coloca chaves com aparência de
inteiro (`"2"`, `"10"`) em ordem numérica antes das demais, o que desfazia a
ordenação. `{"2":0,"9":2,"10":1,"a":3}` deve ser canonicalizado como
`{"10":1,"2":0,"9":2,"a":3}`. Issue #3 do projeto original; a correção foi proposta
no PR #12, fechado sem merge em 13/11/2026.

## 2. O verificador em Python do PR #12 difere do ECMAScript para inteiros grandes

O `scripts/verify-canonical-json.py` mantém inteiros menores que 1e21 com todos os
dígitos. Números JSON são doubles IEEE-754, então o ECMAScript os arredonda:

| entrada | ECMAScript (Node) | verificador do PR #12 |
|---|---|---|
| 9007199254740993 | 9007199254740992 | 9007199254740993 |
| 12345678901234567890 | 12345678901234567000 | 12345678901234567890 |

Em um teste diferencial com 25.822 casos de números contra o Node, 1.673 divergiram,
todos inteiros entre 2^53 e 1e21. Esta implementação converte inteiros para double
primeiro e teve 0 divergências. O PR #12 foi fechado sem merge; o script pode ser
reescrito em um novo PR. O `json.dumps(sort_keys=True)` do próprio Python também
difere do JCS em `500.0`, em `1e-07` e na ordem das chaves para caracteres fora do
BMP.

## 3. Lacunas de verificação na referência (ainda não reportadas)

- `verifyAuthorizationReceipt` confere apenas estrutura e hash; `valid: true` não
  significa que a assinatura foi verificada.
- A assinatura placeholder do emissor de referência (`'ab'.repeat(64)`) passa na
  verificação estrutural. Teste: `test_placeholder_signature_is_rejected`.
- `verifyReceiptChain` não detecta um final removido (a spec documenta isso) e não
  confere onde o primeiro recibo começa, a menos que `prevReceiptHash` seja passado.
  Este repositório acrescenta `expected_head` e `first_sequence`.

## 4. Observações sobre o emissor (reportadas ao projeto original)

Veja a issue sobre o emissor: assinatura placeholder por padrão, `argsRedacted`
copia os argumentos sem redigir e `receiptId` é derivado apenas do nome da
ferramenta e do horário.

## Limites deste trabalho

Testado com um recibo de demonstração e com recibos gerados pelos próprios testes,
não com um conjunto vindo do emissor de referência. A validação de estrutura (tipos
de campos, invariantes semânticas) não está implementada; apenas as verificações
criptográficas.