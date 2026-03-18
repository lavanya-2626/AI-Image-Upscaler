# AI SECURITY RULES

Follow OWASP Top 10 security practices.

Authentication

* Use bcrypt or argon2 for password hashing
* Use JWT or OAuth authentication
* Implement refresh tokens
* Use secure cookies

Input Validation

* Validate all user inputs
* Sanitize HTML inputs
* Prevent injection attacks

Database Security

* Always use parameterized queries
* Never concatenate SQL queries

API Protection

* Implement rate limiting
* Use API authentication
* Prevent brute force attacks

Headers

* Use secure headers
* Use helmet middleware

Secrets

* Never hardcode secrets
* Use environment variables

Logging

* Log security events
* Monitor suspicious activities
