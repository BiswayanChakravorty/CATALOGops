import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { records } = await req.json();
    if (!records || records.length === 0) {
      return NextResponse.json({ error: 'No catalog records provided' }, { status: 400 });
    }

    const findings: any[] = [];
    const skuMap = new Map<string, number[]>();

    records.forEach((row: any, index: number) => {
      const rowNum = index + 1;
      const sku = (row.sku || row.SKU || '').toString().trim();
      const price = row.price || row.Price;
      const category = row.category || row.Category;

      if (sku) skuMap.set(sku, [...(skuMap.get(sku) || []), rowNum]);
      if (price === undefined || price === null || price === '') {
        findings.push({ id: \`missing-price-\${rowNum}\`, issueType: 'Missing Price', sku: sku || \`Row-\${rowNum}\`, row: rowNum, finding: 'Price attribute is blank.' });
      }
      if (!category) {
        findings.push({ id: \`missing-cat-\${rowNum}\`, issueType: 'Missing Category', sku: sku || \`Row-\${rowNum}\`, row: rowNum, finding: 'Category field is blank.' });
      }
    });

    skuMap.forEach((rows, sku) => {
      if (rows.length > 1) rows.forEach(r => findings.push({
        id: \`dup-\${sku}-\${r}\`, issueType: 'Duplicate SKU', sku, row: r,
        finding: \`SKU '\${sku}' appears \${rows.length} times.\`,
      }));
    });

    return NextResponse.json({ rowsAnalyzed: records.length, findingsCount: findings.length, findings });
  } catch (err: any) {
    return NextResponse.json({ error: 'Audit processing failed', details: err.message }, { status: 500 });
  }
}
