<div align="right">
  <a href="FINDINGS.md">🇺🇸 Read in English</a>
</div>

# Achados de uma segunda implementação

Notas de quem implementou um verificador de recibos ADAP em Python a partir da
especificação pública e depois conferiu as correções do mantenedor. Cada item diz
como reproduzir. Os itens 1, 2 e 4 foram reportados ao projeto original e fechados
como corrigidos pelo mantenedor. Última revisão: 14/11/2026.

## 1. Chaves com aparência de inteiro eram ordenadas pela ordem de inserção (reportado, corrigido)

Na referência em TypeScript, `canonicalReceiptJson` ordenava as chaves e depois as
copiava para um objeto JavaScript comum. O JavaScript coloca chaves com aparência de
inteiro (`"2"`, `"10"`) em ordem numérica antes das demais, o que desfazia a
ordenação. `{"2":0,"9":2,"10":1,"a":3}` deve ser canonicalizado como
`{"10":1,"2":0,"9":2,"a":3}`.

Issue #3 do projeto original. O PR #12 foi fechado sem merge; a issue foi depois
fechada como corrigida via PR #18. Os vetores de teste compartilhados, já
atualizados, incluem esse caso, e esta implementação passa nos 18.

## 2. Inteiros grandes: o verificador em Python divergia do ECMAScript (reportado, vetores atualizados)

O verificador em Python do PR #12 mantinha inteiros menores que 1e21 com todos os
dígitos. Números JSON são doubles IEEE-754, então o ECMAScript os arredonda:

| entrada | ECMAScript (Node) | verificador do PR #12 |
|---|---|---|
| 9007199254740993 | 9007199254740992 | 9007199254740993 |
| 12345678901234567890 | 12345678901234567000 | 12345678901234567890 |

Em um teste diferencial com 25.822 casos de números contra o Node, 1.673 divergiram,
todos inteiros entre 2^53 e 1e21. Esta implementação converte inteiros para double
primeiro e teve 0 divergências. O `json.dumps(sort_keys=True)` do próprio Python
também difere do JCS em `500.0`, em `1e-07` e na ordem das chaves para caracteres
fora do BMP.

Os vetores atualizados agora dizem que inteiros acima de 2^53 são arredondados como
o `Number` do JavaScript e incluem `9007199254740993` e `12345678901234567890`. Esta
implementação coincide com os vetores e com o Node nesses casos. Não inspecionei o
novo script Python do projeto, só os vetores.

## 3. Lacunas de verificação na referência (parcialmente tratadas, não reportadas)

- `verifyAuthorizationReceipt` conferia apenas estrutura e hash; `valid: true` não
  significava que a assinatura foi verificada. O mantenedor diz que o verificador
  agora nunca trata uma assinatura placeholder como válida. Não inspecionado.
- `verifyReceiptChain` não detecta um final removido (a spec documenta isso) e não
  confere onde o primeiro recibo começa, a menos que `prevReceiptHash` seja passado.
  O mantenedor agora documenta que o checkpoint externo é responsabilidade de quem
  usa. Este repositório acrescenta `expected_head` e `first_sequence`.

## 4. Observações sobre o emissor (reportadas, corrigidas)

Reportadas na issue #15 do projeto original: assinatura placeholder por padrão,
`argsRedacted` copiando os argumentos sem redigir, `receiptId` derivado apenas do
nome da ferramenta e do horário, e estado da cadeia deixado para quem chama.

A issue #15 foi fechada após o PR #23. Lendo o código novo do emissor (sem executar):

| Ponto | O que o código faz |
|---|---|
| Assinatura placeholder | A emissão falha sem `signer`, `signatureHex` ou `demo: true` |
| Redação de argumentos | Lista de permissão por padrão; copiar tudo exige `includeArgsUnredacted: true` |
| `receiptId` | Inclui 16 bytes aleatórios |
| Estado da cadeia | `AuthorizationReceiptLog` cuida de `sequence` e `prevReceiptHash` em memória |
| Assinatura | `signReceipt` e `signReceiptBytes` estão exportados |

## 5. Observações em aberto (não reportadas)

- `signatureHex` aceita o valor do placeholder (`'ab'.repeat(64)`) sem exigir
  `demo: true`. Um comentário no código diz que o verificador o rejeita; não vi o
  verificador. Baixa gravidade.
- `argsHash` é um hash sem sal dos argumentos completos, então valores de espaço
  pequeno (por exemplo `amount: 500`) poderiam ser adivinhados testando candidatos,
  mesmo quando `argsRedacted` os esconde. É uma observação de design, não um bug.

## Limites deste trabalho

Testado com um recibo de demonstração e com recibos gerados pelos próprios testes,
não com um conjunto vindo do emissor de referência. A validação de estrutura (tipos
de campos, invariantes semânticas) não está implementada; apenas as verificações
criptográficas. O emissor novo foi lido, não executado, e o novo script Python do
projeto não foi inspecionado.
