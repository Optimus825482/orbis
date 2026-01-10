# ORBIS - Play Store Data Safety Form

Bu dosya, Google Play Console'daki Data Safety formunu doldururken referans olarak kullanılabilir.

## Data Collection

### Personal Info

| Data Type | Collected   | Shared | Purpose           |
| --------- | ----------- | ------ | ----------------- |
| Name      | ✅ Optional | ❌ No  | App functionality |
| Email     | ❌ No       | ❌ No  | -                 |
| Phone     | ❌ No       | ❌ No  | -                 |

### Location

| Data Type            | Collected | Shared | Purpose                              |
| -------------------- | --------- | ------ | ------------------------------------ |
| Approximate location | ✅ Yes    | ❌ No  | App functionality (transit analysis) |
| Precise location     | ❌ No     | ❌ No  | -                                    |

### Personal Info (Sensitive)

| Data Type     | Collected | Shared | Purpose                         |
| ------------- | --------- | ------ | ------------------------------- |
| Date of birth | ✅ Yes    | ❌ No  | App functionality (birth chart) |
| Birth time    | ✅ Yes    | ❌ No  | App functionality (birth chart) |
| Birth place   | ✅ Yes    | ❌ No  | App functionality (birth chart) |

### Device Info

| Data Type  | Collected | Shared   | Purpose     |
| ---------- | --------- | -------- | ----------- |
| Device ID  | ✅ Yes    | ✅ AdMob | Advertising |
| Crash logs | ✅ Yes    | ❌ No    | Analytics   |

### App Activity

| Data Type        | Collected | Shared | Purpose   |
| ---------------- | --------- | ------ | --------- |
| App interactions | ✅ Yes    | ❌ No  | Analytics |
| In-app search    | ❌ No     | ❌ No  | -         |

## Data Handling

### Security

- ✅ Data is encrypted in transit (HTTPS/TLS)
- ✅ Data is encrypted at rest
- ✅ You can request that data be deleted

### Data Deletion

Users can request data deletion by:

- Email: privacy@orbis.app
- In-app: Settings > Delete My Data

## Third-Party Services

### Google AdMob

- Purpose: Advertising
- Data shared: Device ID, Ad interactions
- Privacy Policy: https://policies.google.com/privacy

### OpenAI/Anthropic (AI Services)

- Purpose: AI-powered interpretations
- Data shared: Birth data (anonymized, no personal identifiers)
- Note: Data is not linked to user identity

## Compliance

- ✅ GDPR compliant
- ✅ KVKK (Turkish Data Protection Law) compliant
- ✅ COPPA compliant (13+ age requirement)

## Contact

Data Protection Officer: privacy@orbis.app
