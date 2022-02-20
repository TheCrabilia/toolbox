# Generate X.509 certificate

Options:

```text
-h, --help                    Show help
-c CONFIG, --config CONFIG    Path to config file (default: config/main.yaml)
--ca-name CA_NAME             Name of existing CA certificate (optional)
```

## Config file

Global configuration contains parameters ralated to all certificates, that will be generated.

Parameters:

- `country` - country code (required)
- `state` - name of state (required)
- `locality` - name of locality (required)
- `orgatization` - name of organization (required)

```yaml
global:
    country: US
    state: New York
    locality: New York
    organization: some-organization.xyz
```

Certificates configuration contains list of parameters related to each certificate.

Parameters:

- `name` - name of the certificate (required)
- `ca` - weather certificate should be threated like CA certificate or not (optional, default: `false`)
- `commonName` - common name of the certificate (optional, default: certificate name)
- `subjectAltNameType` - type of subject alternamive name, accepted values are `DNS`, `email`, `IP` (required)
- `keySize` - key size, used to generate certificate (optional, default: `2048`)
- `daysValid` - number of days certificate should be valid (optional, default: `365`)
- `keyUsage` - list of key usage types, list of accepted values (required)
- `trusted` - weather certificate should be trusted or not (optional, default: `no`)

> Note: All number values should be a string (quoted).

```yaml
certificates:
  - name: ca-certificate
    subjectAltNameType: DNS
    keySize: "2048"
    daysValid: "365"
    keyUsage:
      - digital-signature
      - key-encipherment
      - data-encipherment
      - key-cert-sign
      - crl-sign
```

## List of accepted key usage types

- code-sign
- content-commitment
- crl-sign
- data-encipherment
- decipher-only
- digital-signature
- dvcs
- email-protect
- encipher-only
- ipsec-end-system
- ipsec-tunnel
- ipsec-user
- key-agreement
- key-cert-sign
- key-encipherment
- ocsp-sign
- server-gated-crypto
- timestamp
- tls-client
- tls-server
