# CATALOGops Web MVP (0.1)

Browser-based CSV audit interface built with Vite + React. Catalog rows are parsed and audited in the browser; no catalog upload endpoint, authentication, persistent workspace, or database is included in this first web build.

## Deploy to Vercel (no terminal required)
1. Open Vercel and choose **Add New → Project**.
2. Import the GitHub repository `BiswayanChakravorty/CATALOGops`.
3. Select branch `main-mvp-web-0.01` in project settings.
4. Framework preset: **Vite**. Build command: `npm run build`; output directory: `dist`.
5. Click **Deploy**. Vercel will provide a public URL.

## Included
- Responsive company-style dashboard
- CSV import and in-browser checks: duplicate SKU, missing SKU/title/price/category, repeated normalized titles, invalid prices
- Findings search and issue filter
- CSV findings export and browser print / Save as PDF
- Sample catalog demonstration

## Important MVP limitations
CSV only; no XLSX support, user accounts, tenant isolation, cloud persistence, audit history, live store integrations, fuzzy title matching, advanced variant detection, or automated fixes. The app should not be represented as an enterprise-secure multi-company SaaS until authentication, access control, retention policy, and server-side protections are implemented.
