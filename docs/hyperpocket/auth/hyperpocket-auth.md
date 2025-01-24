# Hyperpocket Auth

Hyperpocket provides a robust and flexible authentication flow to support secure interactions with external tools and APIs. It enables **multi-turn authentication**, ensures the safety of sensitive data, and integrates seamlessly with various AI agent frameworks. By supporting multiple authentication scenarios, Hyperpocket removes the need for static user credentials and provides dynamic, secure authentication tailored to different workflows.

## Advantages of Hyperpocket Auth

- **Security**: Tokens and sensitive data are securely managed, reducing the risk of leaks.
- **Simplicity**: No need to manage additional server infrastructure; the internal auth server does it all.
- **Flexibility**: Works across different tools and agent frameworks, supporting various workflows.
- **Compatibility**: Handles multi-account scenarios with ease, enabling more complex use cases.

## Supported authentication scenarios

Hyperpocket supports two authentication flows: token-based auth and OAuth2. The OAuth2 flow includes token issuance, callback handling, and multi-account support, while token-based authentication allows tokens and static information to be passed securely as environment variables.
