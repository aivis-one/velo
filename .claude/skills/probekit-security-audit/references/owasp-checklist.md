# OWASP Top 10 — Detection Checklist

Structured checklist for code-level security scanning.
Only includes patterns detectable by reading source code.

---

## A01: Broken Access Control

**What to check:**
- Direct object access by ID without owner filter (IDOR)
- Endpoints missing auth middleware/decorator
- Role checks using string comparison instead of enum
- `os.path.join()` with user input (path traversal)
- Admin functions without role verification

**Detection signals:**
- `Model.objects.get(id=<user_input>)` without `.filter(user=request.user)`
- Route handler without `@login_required` / `authMiddleware`
- `req.params.id` used directly in DB query without owner check
- `os.path.join(base, user_input)` without `os.path.realpath` validation
- Auth/gate check that returns 401/403 but AFTER the handler already ran (state mutated,
  then rejected). Audit the ORDER: the credential check must precede any payload
  processing / DB write / side effect.
- Test smell: a fail-closed test asserts only the status code (401/403) and never asserts
  the downstream handler was NOT invoked. A correct test asserts
  `handler.assert_not_called()` (no side effect) on the absent/invalid-credential path.
  // discovered S20 P110 (domestic-SMS webhook — assert_not_called before processing)

**Severity:** 🔴 for IDOR, missing auth on write ops, path traversal to system files,
and gates that mutate-then-reject (side effect occurs before the 401). 🟡 for missing
auth on read-only public-like resources.

---

## A02: Cryptographic Failures

**What to check:**
- Passwords hashed with MD5/SHA1/SHA256 (without bcrypt/argon2)
- Hardcoded encryption keys or secrets
- TLS verification disabled (`verify=False`, `rejectUnauthorized: false`)
- `random` module used for security tokens (should use `secrets`/`crypto`)
- ECB mode in symmetric encryption
- External webhook endpoints without HMAC/signature verification

**Detection signals:**
- `hashlib.md5(password)`, `hashlib.sha1(password)`
- `SECRET_KEY = "literal_string"`, `ENCRYPTION_KEY = b"..."`
- `requests.get(url, verify=False)`
- `AES.new(key, AES.MODE_ECB)`
- `random.randint()` for token/OTP generation
- Route handler accepting provider webhooks (SMS, payments, CI, chat) WITHOUT `hmac.compare_digest` / `crypto.timingSafeEqual` against a provider-specific signature header

**Severity:** 🔴 for plaintext/weak password hashing, hardcoded keys, disabled TLS, unauthenticated external webhooks. 🟡 for weak algorithms in non-critical paths.

### HMAC defer-don't-guess rule (external webhooks)

When a webhook endpoint is found without signature verification AND the provider's HMAC algorithm / signing-key-header spec is unknown or unavailable to the auditor, **the finding is logged as CRITICAL but the fix is DEFERRED, not auto-generated.** The code-audit pipeline MUST NOT:

- Synthesize an HMAC verification block using a guessed algorithm (e.g. "probably HMAC-SHA256 of raw body with header `X-Signature`"). SMS providers in particular vary: some sign `timestamp + body`, some sign `body` only, some use hex digest, some base64, some prepend `sha256=`. A guessed verifier either accepts everything (algorithm mismatch fails-open on some provider variants) or rejects everything (locks the user out).
- Provision a placeholder `WEBHOOK_SECRET=CHANGEME` in config and mark the finding resolved. That creates a silent fails-open where every unsigned request passes comparison against the placeholder if the verifier is written wrong.
- Close the finding with "user to configure HMAC" — the vulnerability persists until actual verification code runs.

**Required deferral shape:**
1. Keep the finding at CRITICAL severity. Do NOT downgrade.
2. Route to BACKLOG with explicit entry: provider name, endpoint path, provider doc link (if findable), list of unknowns (algorithm? key-header? payload-canonicalization?).
3. Block deploy-readiness gate until the backlog item is resolved with provider-confirmed spec — not a probekit guess.
4. Note in the report methodology: "HMAC verification deferred — provider spec not available to auditor. Guessing the algorithm introduces strictly-worse fails-open / fails-closed failure modes than leaving the known-missing state visible."

Canonical case: BG-S14 Step 6 F4 — domestic SMS webhook endpoint publicly reachable via nginx catch-all, no HMAC verification. Scout directive was "do NOT guess algorithm"; finding deferred as `SEC-S14-85` BACKLOG entry. Rationale: provider's webhook spec + signing key were not provisioned at audit time, and the three plausible HMAC variants (raw-body-sha256, timestamp+body-sha256, form-encoded-fields-signed) have non-overlapping verification code — wrong choice either accepts all unsigned traffic (fails-open) or rejects all legitimate traffic (fails-closed, breaking the integration). Deferred-as-CRITICAL keeps the gap visible; auto-generated-guess would have buried it.

---

## A03: Injection

**What to check:**
- SQL: string concatenation/f-string in SQL queries
- Command: `os.system()`, `subprocess.call(shell=True)` with user input
- XSS: user input rendered without escaping in templates
- Template injection: user input in template string
- LDAP/XML injection patterns

**Detection signals:**
- `f"SELECT * FROM users WHERE id = {user_input}"`
- `cursor.execute("... WHERE name = '" + name + "'")`
- `os.system(f"convert {filename}")`, `subprocess.call(cmd, shell=True)`
- `|safe` filter on user input in Jinja2/Django templates
- `render_template_string(user_input)`

**Severity:** 🔴 for SQL injection, command injection, template injection. 🟡 for potential XSS with partial escaping.

---

## A04: Insecure Design

**What to check:**
- No rate limiting on auth endpoints
- No input validation framework (Pydantic, Joi, etc.)
- Business logic without abuse prevention
- Missing account lockout after failed attempts

**Detection signals:**
- Login endpoint without rate limit middleware
- `request.body` / `req.body` used directly without schema validation
- Password reset without token expiration

**Severity:** 🟡 for most design issues (they are patterns, not specific vulns).

---

## A05: Security Misconfiguration

**What to check:**
- `DEBUG = True` in production config
- `CORS(app, origins="*")` or `Access-Control-Allow-Origin: *`
- `ALLOWED_HOSTS = ['*']`
- Verbose error messages exposing stack traces
- Default credentials in config files

**Detection signals:**
- `DEBUG = True` outside test/dev files
- `cors({ origin: '*' })` or `CORS_ALLOW_ALL_ORIGINS = True`
- `app.use(errorHandler)` that sends `err.stack` to client

**Severity:** 🔴 for debug in prod, default credentials. 🟡 for overly permissive CORS, verbose errors.

---

## A07: Auth Failures

**What to check:**
- JWT decoded without signature verification
- Session without expiration/timeout
- Password stored in plaintext or reversible encoding
- Missing brute-force protection on login

**Detection signals:**
- `jwt.decode(token, options={"verify_signature": False})`
- `jwt.decode(token, algorithms=["none"])`
- Session config without `expires` or `maxAge`
- `base64.b64encode(password)` as "encryption"

**Severity:** 🔴 for JWT without verification, plaintext passwords. 🟡 for missing session expiration.

---

## A08: Data Integrity

**What to check:**
- Insecure deserialization (`pickle.loads`, `yaml.load` without SafeLoader)
- Missing CSRF protection on state-changing endpoints
- `eval()` / `exec()` on user-controlled input

**Detection signals:**
- `pickle.loads(user_data)`, `pickle.load(open(user_file))`
- `yaml.load(data)` without `Loader=yaml.SafeLoader`
- `eval(request.data)`, `exec(user_input)`
- Forms without CSRF token in non-API web apps

**Severity:** 🔴 for pickle/yaml deserialization of user input, eval/exec. 🟡 for missing CSRF on low-risk forms.

---

## A09: Logging Failures

**What to check:**
- Security events not logged (failed login, auth failures, access denied)
- PII/secrets in log output
- No log for admin actions

**Detection signals:**
- Login handler without `logger.warning("failed_login", ...)`
- `logger.info(f"User data: {user}")` with full user object
- `print(password)`, `logger.debug(f"token={token}")`

**Severity:** 🟡 for missing security logging. 🔴 for secrets/passwords in logs.

---

## A10: SSRF

**What to check:**
- URL from user input passed to HTTP client without validation
- Internal service URLs constructable from user input
- Redirect URL from user input without allowlist

**Detection signals:**
- `requests.get(request.args['url'])`
- `fetch(req.body.webhookUrl)`
- `http.Get(userProvidedURL)` without URL validation
- Redirect: `redirect(request.args.get('next'))` without domain check

**Severity:** 🔴 for unvalidated URL fetch from user input. 🟡 for redirect without allowlist.
