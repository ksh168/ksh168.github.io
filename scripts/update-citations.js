const https = require('https');
const fs = require('fs');
const path = require('path');

// Add delay to avoid rate limiting
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Fetches citation count from the Semantic Scholar API using a DOI.
 * This is a free, public API that doesn't require scraping or API keys.
 * API docs: https://api.semanticscholar.org/graph/v1
 * @param {string} doi - The DOI of the paper (e.g. "10.1109/...")
 * @returns {Promise<number|null>} - The citation count, or null on failure
 */
async function fetchCitationsFromSemanticScholar(doi) {
    return new Promise((resolve) => {
        const url = `https://api.semanticscholar.org/graph/v1/paper/DOI:${encodeURIComponent(doi)}?fields=citationCount`;
        console.log(`  Fetching: ${url}`);

        const req = https.get(url, {
            headers: {
                'User-Agent': 'citation-updater-bot/1.0 (personal portfolio; contact via GitHub ksh168)',
            }
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        const parsed = JSON.parse(data);
                        resolve(parsed.citationCount ?? null);
                    } catch (e) {
                        console.error(`  Parse error for DOI ${doi}:`, e.message);
                        resolve(null);
                    }
                } else if (res.statusCode === 404) {
                    console.warn(`  DOI not found on Semantic Scholar: ${doi}`);
                    resolve(null);
                } else if (res.statusCode === 429) {
                    console.warn(`  Rate limited by Semantic Scholar (429). Retrying after delay...`);
                    resolve('RATE_LIMITED');
                } else {
                    console.error(`  Unexpected status ${res.statusCode} for DOI ${doi}`);
                    resolve(null);
                }
            });
        });

        req.on('error', (err) => {
            console.error(`  Network error for DOI ${doi}:`, err.message);
            resolve(null);
        });

        req.setTimeout(15000, () => {
            console.error(`  Request timed out for DOI ${doi}`);
            req.destroy();
            resolve(null);
        });
    });
}

async function updateCitations() {
    const dataPath = path.join(__dirname, '../src/data/data.json');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

    let updatedCount = 0;

    for (const pub of data.publications) {
        // Extract the DOI from the doi field (strip the https://doi.org/ prefix if present)
        if (!pub.doi) {
            console.log(`Skipping "${pub.title}" — no DOI found.`);
            continue;
        }

        const doi = pub.doi.replace(/^https?:\/\/doi\.org\//i, '');
        console.log(`\nUpdating citations for: "${pub.title}"`);
        console.log(`  DOI: ${doi}`);

        let citations = await fetchCitationsFromSemanticScholar(doi);

        // Handle rate limiting with a longer back-off
        if (citations === 'RATE_LIMITED') {
            console.log('  Waiting 30s before retry...');
            await delay(30000);
            citations = await fetchCitationsFromSemanticScholar(doi);
        }

        if (citations !== null && citations !== 'RATE_LIMITED') {
            pub.citations = citations;
            pub.lastUpdated = new Date().toISOString();
            console.log(`  ✅ Updated citations: ${citations}`);
            updatedCount++;
        } else {
            console.log(`  ⚠️  Could not fetch citations — keeping existing value (${pub.citations ?? 'none'}).`);
        }

        // Be respectful: wait 3 seconds between requests
        await delay(3000);
    }

    // Write updated data back to file
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2));
    console.log(`\nDone! Updated ${updatedCount}/${data.publications.length} publications.`);
}

updateCitations().catch((err) => {
    console.error('Fatal error:', err);
    process.exit(1);
});