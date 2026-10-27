# Certificate Verification (Format 2)

This document is the canonical, implementation-neutral description of how an
Aegean Commercial License certificate is canonicalized and checked. It exists so
a third party can implement a verifier without reading the Python source, and so
the website verifier and the Python verifier can be tested against the same bytes.

**Trust model.** A certificate's SHA-256 digest proves only that its record is
internally consistent; anyone can recompute a digest. Authenticity comes from the
public register at `licenses/issued.json`: a certificate is evidence of a grant
only when its id and digest are listed there as `valid`. The issuer's HMAC
signature is a keyed hash that only AegeanWorks can check; the signing key is
never published. Publishing that key would let anyone forge a certificate, so a
public verifier must never ask for it and must never implement the signature check.

## Canonical payload

Starting from the parsed certificate object:

1. Remove the top-level `digest` and `signature` fields.
2. If `projects` is present and is an array, sort it ascending. Other arrays keep
   their order.
3. Serialize with all object keys sorted ascending, no insignificant whitespace,
   and only ASCII output (non-ASCII characters escaped as lowercase `\uXXXX`,
   including surrogate pairs). In Python this is exactly:

   ```python
   import json
   payload = json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
   ```

   This is the byte sequence a JavaScript implementation must reproduce, including
   escaping of non-ASCII text such as `ı`, `ü` and `—`.

## Digest

The certificate digest is the lowercase hexadecimal SHA-256 of:

```text
aegean-certificate/2\n
```

followed by the UTF-8 bytes of the canonical payload. The literal prefix and the
newline are part of the hashed bytes.

## Verification order

A verifier should return the first applicable status:

1. `UNSUPPORTED_FORMAT` — `format` is not the integer `2` (format 1 is retired).
2. `TAMPERED` — `digest` is missing.
3. `INVALID_FORMAT` — a field has the wrong JSON type: `projects` is not a string or a list of
   strings, `allowances` is not a string or a list of strings, `expires_at` is neither a string nor
   null, or `is_perpetual` is not a boolean. These checks come before canonicalization because a
   mixed list cannot be sorted safely.
4. `TAMPERED` — `digest` does not equal the computed digest.
5. `INVALID_FORMAT` — `serial` is not exactly 64 lowercase hexadecimal characters.
6. `INVALID_FORMAT` — the license type is unknown, the tier is not defined by that agreement, an
   allowance is not in the agreement vocabulary, or a non-empty `terms_digest` does not match the
   published agreement text.
7. `UNREGISTERED` — the id is absent from the register, or the register's digest for that id
   differs from the certificate digest.
8. `REVOKED` — the register lists the id as revoked.
9. `INVALID_FORMAT` — a perpetual certificate has `expires_at`, or a term-limited certificate has
   no `expires_at`, or a date is not a real `YYYY-MM-DD` date.
10. `EXPIRED` — the reference date is after `expires_at`.
11. `SCOPE_MISMATCH` — a project was requested and is not in `projects` (`*` covers every project).
12. `VALID` — all checks passed and the register entry is valid.

The public verifier must use the register copy from this repository, not a copy
supplied alongside a certificate. A missing, unreadable or malformed register is
an error, not an empty register. A register entry with an unknown `status` is
malformed; only `valid` and `revoked` are understood.

The certificate digest and the HMAC signature are different checks. The public
register is the public proof; the signature is checked only in AegeanWorks'
private operations tooling, which requires both the register and the signing key.

## Conformance vector

[`licenses/verification-vector.json`](verification-vector.json) is a **fixture, not
an issued certificate**. It pins canonicalization, escaping and the domain prefix:

- expected digest: `855969a9506d23f8f5e0553a63f61f277329018bfc7c8d7fb1c40fba6eda52ff`
- certificate id: `conformance-vector-0001`
- it is deliberately absent from the public register

Its fields include Turkish characters, an em dash, a quote, an escaped newline and
unsorted project names, so a verifier that differs on `ensure_ascii`, key sorting
or project sorting fails the vector. The Python test is
`tests/test_verification_spec.py`; the website's Node test uses the same vector.

## Handling untrusted input

A verifier should cap the input size, parse JSON strictly, read only known fields,
and render every certificate value as text rather than HTML. It should fetch the
register over HTTPS from the canonical repository and show when it was fetched, so
a stale cached revocation is visible to the user. These are implementation rules,
not alternatives to the checks above.
