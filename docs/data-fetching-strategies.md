# Data Fetching Strategies for Semble Integration (Generated with Claude Code)

This guide compares different approaches for fetching and displaying data from the Semble API in the AT Science homepage.

## Current Implementation: Build-Time Fetching

### How It Works
- Eleventy's `_data/sembleProjects.js` fetches data during the build process
- Data is embedded into static HTML files
- Pages are served as pre-rendered static content

### Implementation
Already implemented in `content/_data/sembleProjects.js:18-51`

### Pros
- **Fast page loads** - No API calls at runtime, just static HTML
- **SEO-friendly** - Search engines can crawl all project data
- **Reliable** - Works without JavaScript
- **No API exposure** - API endpoints not visible to end users
- **Simple** - Leverages Eleventy's native data fetching

### Cons
- **Stale data** - Requires rebuild to reflect Semble changes
- **Dev server doesn't auto-refresh** - Need to restart to see updates
- **Build-time dependency** - Site build fails if Semble API is down

### Best For
- Content that doesn't change frequently
- SEO is important
- Fast page loads are critical
- Current use case (projects list updated occasionally)

---

## Option 1: Client-Side Fetching

### How It Works
- Page loads with empty/placeholder content
- JavaScript fetches from Semble API in the browser
- DOM is updated with fresh data on every page load

### Implementation Outline

**1. Modify `content/_data/sembleProjects.js`:**
```javascript
export default async function() {
  return []; // Empty array, fetch client-side instead
}
```

**2. Create `content/assets/scripts/dynamic-projects.js`:**
```javascript
async function fetchProjects() {
  const response = await fetch('https://api.semble.so/api/...');
  const data = await response.json();
  // Transform and return projects
}

function renderProjects(projects) {
  // Build HTML and inject into DOM
}

document.addEventListener('DOMContentLoaded', async () => {
  const projects = await fetchProjects();
  renderProjects(projects);
});
```

**3. Update page template:**
```html
<div id="projects-container">Loading...</div>
<script src="/assets/scripts/dynamic-projects.js"></script>
```

### Pros
- **Always fresh** - Data updates on every page load without rebuild
- **Fast deploys** - No need to rebuild for content changes
- **Simple implementation** - Just JavaScript, no server changes

### Cons
- **API exposure** - Semble API URL visible in browser dev tools (security/rate limiting concern)
- **CORS dependency** - Requires Semble API to allow cross-origin requests
- **No SEO** - Search engines won't see dynamically loaded content
- **Slower perceived load** - Users see "Loading..." before content appears
- **JavaScript required** - Fails for users with JS disabled
- **Multiple requests** - Each visitor hits Semble API directly

### Best For
- Internal tools or admin dashboards
- Frequently changing data (real-time updates)
- SEO is not important
- You control both client and API (can handle CORS)

---

## Option 2: Scheduled Rebuilds

### How It Works
- Keep current build-time fetching approach
- Configure hosting platform to rebuild automatically on a schedule
- E.g., rebuild every hour, every 6 hours, or daily

### Implementation

**Netlify:**
```yaml
# netlify.toml
[build]
  command = "npm run build"

[build.environment]
  # Trigger builds via Netlify's scheduled builds feature
  # Configure in UI: Site settings > Build & deploy > Build hooks
```

Create a build hook URL, then use a service like:
- **Netlify's scheduled functions** (built-in)
- **GitHub Actions** with cron schedule
- **External cron service** (e.g., cron-job.org, EasyCron)

**GitHub Actions Example:**
```yaml
# .github/workflows/scheduled-build.yml
name: Scheduled Rebuild

on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Netlify Build
        run: |
          curl -X POST -d {} https://api.netlify.com/build_hooks/YOUR_HOOK_ID
```

**Vercel:**
```yaml
# vercel.json - No native cron, use external service
# Or use Vercel's Deploy Hooks with GitHub Actions
```

### Pros
- **No code changes** - Uses existing implementation
- **Predictable freshness** - Know exactly how stale data can be
- **Maintains SEO** - Still static HTML
- **No API exposure** - API stays server-side
- **Simple setup** - Just configure hosting platform

### Cons
- **Unnecessary builds** - Rebuilds even when data hasn't changed
- **Still has lag** - Up to [schedule interval] between update and visibility
- **Build minutes cost** - Uses hosting platform build quota
- **Not truly real-time** - Fixed schedule, not event-driven

### Best For
- Content that updates regularly but not constantly
- Want to keep current architecture
- SEO is important
- Can tolerate scheduled refresh (e.g., hourly updates)

---

## Option 3: Webhook-Triggered Rebuilds

### How It Works
- Keep current build-time fetching approach
- Semble sends webhook when collection changes
- Webhook triggers immediate site rebuild
- Fresh data appears within minutes

### Implementation

**1. Create build hook in hosting platform:**

**Netlify:**
- Go to: Site settings > Build & deploy > Build hooks
- Click "Add build hook"
- Get URL like: `https://api.netlify.com/build_hooks/YOUR_HOOK_ID`

**Vercel:**
- Go to: Project settings > Git > Deploy Hooks
- Create hook
- Get URL like: `https://api.vercel.com/v1/integrations/deploy/YOUR_HOOK_ID`

**2. Configure Semble webhook (if supported):**
```
Webhook URL: [Your build hook URL]
Trigger: On collection update
Method: POST
```

**3. Optional - Add middleware for security:**
```javascript
// netlify/functions/rebuild-trigger.js
export async function handler(event) {
  // Verify webhook signature
  const signature = event.headers['x-semble-signature'];
  if (!verifySignature(signature, event.body)) {
    return { statusCode: 403, body: 'Invalid signature' };
  }

  // Trigger actual build hook
  await fetch(process.env.BUILD_HOOK_URL, { method: 'POST' });
  return { statusCode: 200, body: 'Build triggered' };
}
```

### Pros
- **Event-driven** - Only rebuilds when data actually changes
- **No code changes** - Uses existing implementation
- **Maintains SEO** - Still static HTML
- **Fast updates** - New content appears within 2-5 minutes
- **No API exposure** - API stays server-side
- **Efficient** - No unnecessary builds

### Cons
- **Depends on Semble webhooks** - Semble may not support webhooks
- **Still not instant** - Build takes time (2-5 minutes)
- **Setup complexity** - Requires webhook configuration
- **Potential webhook reliability** - Missed webhooks = missed updates

### Best For
- **IDEAL FOR YOUR USE CASE** if Semble supports webhooks
- Want freshness without unnecessary rebuilds
- SEO is important
- Can tolerate 2-5 minute delay

---

## Option 4: Serverless Functions (Hybrid Approach)

### How It Works
- Remove static data fetching
- Create serverless function to fetch from Semble
- Function caches data for N minutes
- Client fetches from your function (not directly from Semble)
- Optionally: Render initial data at build time, then refresh client-side

### Implementation

**1. Create serverless function:**

**Netlify Function (`netlify/functions/projects.js`):**
```javascript
const fetch = require('node-fetch');

// In-memory cache (lives for function instance lifetime)
let cache = null;
let cacheTime = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

function parseNoteFields(noteText) {
  if (!noteText) return null;
  try {
    const parsed = JSON.parse(noteText);
    return typeof parsed === 'object' ? parsed : null;
  } catch (e) {
    return null;
  }
}

exports.handler = async function(event, context) {
  // Return cached data if fresh
  if (cache && cacheTime && Date.now() - cacheTime < CACHE_DURATION) {
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300'
      },
      body: JSON.stringify(cache)
    };
  }

  try {
    const response = await fetch(
      'https://api.semble.so/api/collections/at/atproto.science/3m5f7jpl6pk2j?page=1&limit=100&sortBy=createdAt&sortOrder=desc'
    );

    if (!response.ok) {
      throw new Error('Failed to fetch from Semble');
    }

    const data = await response.json();

    const projects = data.urlCards.map(card => {
      const noteFields = parseNoteFields(card.note?.text);
      return {
        url: card.url,
        date: card.createdAt,
        data: {
          title: noteFields?.title || card.cardContent?.title || 'Untitled Project',
          description: noteFields?.description || card.note?.text || card.cardContent?.description || ''
        }
      };
    });

    // Update cache
    cache = projects;
    cacheTime = Date.now();

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300'
      },
      body: JSON.stringify(projects)
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch projects' })
    };
  }
};
```

**Vercel Function (`api/projects.js`):**
```javascript
// Same logic as above, Vercel automatically caches function responses
```

**2. Client-side JavaScript:**
```javascript
// content/assets/scripts/projects.js
async function loadProjects() {
  const response = await fetch('/.netlify/functions/projects');
  const projects = await response.json();
  renderProjects(projects);
}

document.addEventListener('DOMContentLoaded', loadProjects);
```

**3. Optional - Hybrid rendering:**
Keep `content/_data/sembleProjects.js` for initial render, add client-side refresh.

### Pros
- **Fresh data** - Updates within cache window (e.g., 5 minutes)
- **No API exposure** - Semble API hidden behind your function
- **Caching control** - Tune freshness vs. performance
- **Better than client-side** - Your function handles CORS, rate limiting
- **Still fast** - Function caches reduce Semble API load
- **No rebuild needed** - Content updates automatically

### Cons
- **Loses SEO** (if fully client-side) - Search engines don't execute JS well
- **JavaScript required** - Fails for users with JS disabled
- **Serverless costs** - Function invocations cost money (usually negligible)
- **More complex** - Requires serverless function setup
- **Slower initial load** - Users see loading state briefly

### Hybrid Variant Pros
- **Maintains SEO** - Initial render has content
- **Fresh data** - Client-side refresh after page load
- **Best of both worlds** - Static HTML + dynamic updates

### Best For
- Need data fresher than hourly rebuilds allow
- Want control over caching and API access
- Willing to add serverless infrastructure
- SEO is somewhat important (use hybrid variant)

---

## Option 5: Edge Functions (Advanced)

### How It Works
- Similar to serverless, but runs at CDN edge
- Renders HTML at edge with fresh data
- Faster than serverless (no cold starts)
- Available on Netlify Edge, Vercel Edge, Cloudflare Workers

### Implementation (Netlify Edge)

```javascript
// netlify/edge-functions/projects.js
export default async (request, context) => {
  const projects = await fetch('https://api.semble.so/...').then(r => r.json());

  // Transform data
  const transformed = transformProjects(projects);

  // Render page with fresh data
  const response = await context.next();
  const page = await response.text();

  // Inject data or return JSON
  return new Response(
    page.replace('<!-- PROJECTS_PLACEHOLDER -->', renderHTML(transformed)),
    response
  );
};

export const config = { path: "/projects" };
```

### Pros
- **Very fast** - No cold starts, runs at CDN edge
- **Fresh data** - Rendered on-demand with caching
- **SEO-friendly** - Server-rendered HTML
- **No JavaScript required** - Works for all users
- **Efficient** - Edge caching reduces API calls

### Cons
- **Most complex** - Requires edge function knowledge
- **Platform-specific** - Different syntax per platform
- **Limited execution time** - Edge functions have strict limits
- **Debugging harder** - Can't test locally as easily

### Best For
- High-traffic sites needing fresh data
- Global audience (edge = fast worldwide)
- Complex caching requirements
- Team comfortable with edge computing

---

## Recommendation Matrix

| Requirement | Best Approach |
|-------------|---------------|
| **Current use case (infrequent updates, SEO important)** | **Build-time (current)** or **Webhook-triggered** |
| **Updates multiple times per day** | **Scheduled rebuilds** (hourly) or **Serverless hybrid** |
| **Near real-time updates needed** | **Serverless functions** or **Edge functions** |
| **SEO is critical** | **Build-time**, **Webhooks**, or **Edge functions** |
| **No rebuild tolerance** | **Client-side** or **Serverless** |
| **Simplest to maintain** | **Build-time (current)** or **Scheduled rebuilds** |
| **Highest performance** | **Build-time (current)** or **Edge functions** |
| **Most flexible** | **Serverless hybrid** |

---

## Decision Guide

**Start with current approach if:**
- Projects update less than daily
- You're okay redeploying to show new projects
- SEO matters

**Add scheduled rebuilds if:**
- Updates are regular (e.g., daily)
- Want automation without code changes
- Build minutes aren't a concern

**Investigate webhooks if:**
- Semble supports them
- Want event-driven updates
- 2-5 minute delay is acceptable

**Consider serverless if:**
- Need updates within minutes
- Want to hide API details
- Comfortable with serverless infrastructure

**Go client-side only if:**
- Internal tool / admin dashboard
- SEO doesn't matter
- Need instant updates

---

## Recommended Path Forward

Given your use case (testing if dynamic project list is useful):

### Phase 1: Stay with current build-time fetching
- Simple, works well for initial testing
- Manually rebuild when adding test projects
- Evaluate if feature is valuable

### Phase 2: If feature proves useful, investigate webhooks
- Check if Semble API supports webhooks
- If yes → implement webhook-triggered rebuilds (best balance)
- If no → implement scheduled rebuilds (hourly or daily)

### Phase 3: If real-time updates become critical
- Implement serverless hybrid approach
- Initial render from build-time data (SEO)
- Client-side refresh from serverless function (freshness)

This approach lets you validate the feature before investing in more complex infrastructure.
