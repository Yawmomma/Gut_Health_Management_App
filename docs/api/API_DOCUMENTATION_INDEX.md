# API Documentation Index

**Complete API Documentation Suite**
**Version**: 1.0.0
**Last Updated**: February 28, 2026

This index guides you to the right documentation for your needs.

---

## 📚 Documentation Files

### 1. **README.md** (START HERE)
- Quick overview of the API
- Installation instructions
- High-level feature list
- Tech stack information
- **Best for**: First-time users, project overview

### 2. **api_endpoint_full_documentation.md** (COMPREHENSIVE REFERENCE)
- Complete guide to 136 endpoints
- Detailed authentication explanation
- Rate limiting details
- Scope reference (all 40 scopes)
- Migration notes for upgrading
- Common use cases with code examples
- Troubleshooting section
- **Best for**: API consumers, developers building integrations

### 3. **api_endpoints.md** (QUICK REFERENCE)
- Quick summary of all 136 endpoints by category
- Endpoint paths and HTTP methods
- Scope requirements
- Brief descriptions
- **Best for**: Quick lookups, checklists

### 4. **API_SDK_EXAMPLES.md** (CODE EXAMPLES)
- Python SDK with complete examples
- JavaScript SDK with complete examples
- Common patterns (retry logic, rate limiting, pagination)
- Error handling code
- Testing examples
- **Best for**: Developers writing code, copy-paste examples

### 5. **postman_collection.json** (INTERACTIVE TESTING)
- Ready-to-import Postman collection
- Pre-configured requests for major endpoints
- Environment variables for API key and base URL
- Example request bodies
- **Best for**: Testing endpoints in Postman/Insomnia, quick prototyping

### 6. **WEBHOOK_REFERENCE.md** (REAL-TIME INTEGRATIONS)
- Complete webhook setup guide
- Event types and payloads
- Server-Sent Events (SSE) explanation
- Signature verification code
- Retry logic explanation
- Best practices and examples
- **Best for**: Building real-time integrations, setting up webhooks

### 7. **DATA_SCHEMA_REFERENCE.md** (DATA STRUCTURES)
- Complete field definitions for all objects
- Data types and constraints
- Examples for each schema
- Enum values (traffic lights, meal types, etc.)
- **Best for**: Understanding data structure, API response format

---

## 🎯 Quick Navigation by Use Case

### I'm a New User
1. Read: README.md (overview)
2. Visit: http://localhost:5000/api/docs (interactive Swagger UI)
3. Read: api_endpoint_full_documentation.md (detailed explanation)

### I'm Building a Python Integration
1. Read: API_SDK_EXAMPLES.md (Python section)
2. Reference: DATA_SCHEMA_REFERENCE.md (data structures)
3. Test: postman_collection.json (validate requests first)
4. Handle: Error handling code in API_SDK_EXAMPLES.md

### I'm Building a JavaScript Integration
1. Read: API_SDK_EXAMPLES.md (JavaScript section)
2. Reference: DATA_SCHEMA_REFERENCE.md (data structures)
3. Test: postman_collection.json (validate requests first)
4. Listen: WEBHOOK_REFERENCE.md (real-time events)

### I'm Setting Up Webhooks
1. Read: WEBHOOK_REFERENCE.md (complete guide)
2. Verify: Signature verification examples (Python/Node.js)
3. Implement: Event handlers for event types you care about
4. Test: Use webhook test endpoint

### I'm Integrating with APP2
1. Read: api_endpoint_full_documentation.md (scopes section)
2. Create: API key using bootstrap script
3. Reference: APP2 scopes in api_endpoint_full_documentation.md
4. Implement: Primary endpoints first, then secondary
5. Monitor: Rate limiting and access logs

### I Need to Debug Something
1. Check: TROUBLESHOOTING section in api_endpoint_full_documentation.md
2. Verify: Your API key and scopes
3. Test: Request in postman_collection.json
4. Read: DATA_SCHEMA_REFERENCE.md to understand response structure
5. Check: Error codes table in api_endpoint_full_documentation.md

---

## 🔍 Finding Specific Information

### API Keys & Authentication
- **Setup**: api_endpoint_full_documentation.md → "Quick Start" section
- **Scopes**: api_endpoint_full_documentation.md → "Scopes Reference"
- **Code examples**: API_SDK_EXAMPLES.md → "API Key Management"

### Diary & Symptom Tracking
- **Endpoints**: api_endpoints.md → "Diary (9 endpoints)"
- **Full reference**: api_endpoint_full_documentation.md → "Diary (9 endpoints)"
- **Schema**: DATA_SCHEMA_REFERENCE.md → "Diary Objects"
- **Examples**: API_SDK_EXAMPLES.md → "Example 2: Track Symptoms"

### Food Search & Comparisons
- **Endpoints**: api_endpoints.md → "Foods & Compendium (14 endpoints)"
- **Full reference**: api_endpoint_full_documentation.md → "Foods & Compendium"
- **Schema**: DATA_SCHEMA_REFERENCE.md → "Food Objects"
- **Examples**: API_SDK_EXAMPLES.md → "Example 3: Search for Safe Foods"

### Analytics & Trends
- **Endpoints**: api_endpoints.md → "Analytics & Dashboard (27 endpoints)"
- **Full reference**: api_endpoint_full_documentation.md → "Analytics (27 endpoints)"
- **Schema**: DATA_SCHEMA_REFERENCE.md → "Analytics Objects"
- **Examples**: API_SDK_EXAMPLES.md → "Example 4: Get Analytics & Trends"

### Recipes & Meals
- **Endpoints**: api_endpoints.md → "Recipes & Meals (15 endpoints)"
- **Full reference**: api_endpoint_full_documentation.md → "Recipes & Meals"
- **Schema**: DATA_SCHEMA_REFERENCE.md → "Recipe Objects"
- **Examples**: API_SDK_EXAMPLES.md → "Example 5: Manage Recipes"

### Real-Time Events
- **Webhooks**: WEBHOOK_REFERENCE.md → "Setting Up Webhooks"
- **Events**: WEBHOOK_REFERENCE.md → "Event Types"
- **SSE**: WEBHOOK_REFERENCE.md → "Server-Sent Events (SSE)"
- **Examples**: WEBHOOK_REFERENCE.md → "Complete Webhook Example"

### Error Handling
- **Codes**: DATA_SCHEMA_REFERENCE.md → "Error Objects"
- **Solutions**: api_endpoint_full_documentation.md → "Troubleshooting"
- **Code examples**: API_SDK_EXAMPLES.md → "Error Handling"

### Rate Limiting
- **Details**: api_endpoint_full_documentation.md → "Rate Limiting"
- **Checking status**: API_SDK_EXAMPLES.md → "Example 6: API Key Management"
- **Handling 429s**: WEBHOOK_REFERENCE.md → "Retry Logic"

---

## 📖 Document Summaries

| Document | Size | Format | Purpose |
|----------|------|--------|---------|
| README.md | ~10 KB | Markdown | Project overview |
| api_endpoint_full_documentation.md | ~150 KB | Markdown | Comprehensive API guide |
| api_endpoints.md | ~30 KB | Markdown | Quick reference |
| API_SDK_EXAMPLES.md | ~100 KB | Markdown + Code | Code examples (Python, JS) |
| postman_collection.json | ~50 KB | JSON | Interactive API testing |
| WEBHOOK_REFERENCE.md | ~80 KB | Markdown + Code | Webhooks & real-time |
| DATA_SCHEMA_REFERENCE.md | ~60 KB | Markdown | Data structures |

---

## 🚀 Getting Started Checklist

- [ ] Read README.md for overview
- [ ] Visit http://localhost:5000/api/docs for interactive docs
- [ ] Create an API key with appropriate scopes
- [ ] Make your first request (try FODMAP categories — no auth needed)
- [ ] Review api_endpoint_full_documentation.md for your use case
- [ ] Copy code examples from API_SDK_EXAMPLES.md
- [ ] Test requests in postman_collection.json before writing code
- [ ] Bookmark DATA_SCHEMA_REFERENCE.md for reference
- [ ] If using webhooks: read WEBHOOK_REFERENCE.md

---

## 📞 Support & Resources

### Documentation
- **This index**: API_DOCUMENTATION_INDEX.md (you are here)
- **Full reference**: api_endpoint_full_documentation.md
- **Data schemas**: DATA_SCHEMA_REFERENCE.md
- **Code examples**: API_SDK_EXAMPLES.md

### Interactive Tools
- **Swagger UI**: http://localhost:5000/api/docs
- **OpenAPI spec**: http://localhost:5000/api/v1/apispec.json
- **Postman collection**: postman_collection.json

### Project Documentation
- **Project guide**: CLAUDE.md
- **Change history**: Version_History.md
- **TODO & roadmap**: TODO.md

---

## 🔄 Version History

**v1.0.0** (February 28, 2026)
- Complete documentation suite
- 136 endpoints documented
- Python and JavaScript examples
- Postman collection
- Webhook guide
- Data schema reference

---

## 📝 Last Updated
February 28, 2026

---

**Quick Links**:
- 🌐 [Interactive API Docs](http://localhost:5000/api/docs)
- 📄 [OpenAPI Spec](http://localhost:5000/api/v1/apispec.json)
- 🐍 [Python Examples](API_SDK_EXAMPLES.md#python-sdk)
- 📜 [JavaScript Examples](API_SDK_EXAMPLES.md#javascript-sdk)
- 🪝 [Webhook Setup](WEBHOOK_REFERENCE.md#setting-up-webhooks)
- 🔑 [API Keys & Auth](api_endpoint_full_documentation.md#authentication--authorization)
