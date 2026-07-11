/**
 * catalog.js — everyday-words → HS lookup (plan §7.2). Hand-mapped, NOT generic classification.
 * @context  Users search in plain Vietnamese/English; we map to HS behind the scenes and show the
 *           code as an educational badge. Covered products drill into data; uncovered ones show a
 *           locked "coming soon — request it" page whose clicks are demand telemetry (plan §7.6).
 * @done     A small curated list (pilot vertical covered; candidate verticals locked) + a
 *           diacritic-insensitive search() so "trà" and "tra" both match.
 * @todo     Grow toward the 30–50 codes across covered verticals as Stage-0/telemetry picks them.
 * @limits   Data + pure search. No I/O.
 * @affects  Used by SearchBox (client) + page.js (covered vs locked routing).
 */

// covered=true means Layer-1 data exists for it today (pilot vertical only).
export const CATALOG = [
  { hs6: "440131", covered: true,  name_en: "Wood pellets",   name_vi: "Viên nén gỗ",
    synonyms: ["wood pellet", "pellet", "viên nén", "vien nen", "biomass", "chất đốt sinh khối"] },
  { hs6: "4407",   covered: true,  name_en: "Sawn wood",      name_vi: "Gỗ xẻ",
    synonyms: ["sawn wood", "timber", "lumber", "gỗ xẻ", "go xe", "wood", "sawnwood"] },
  { hs6: "090240", covered: true,  name_en: "Black tea",      name_vi: "Chè (trà) đen",
    synonyms: ["tea", "black tea", "trà", "tra", "chè", "che"] },
  { hs6: "090111", covered: true,  name_en: "Coffee",         name_vi: "Cà phê",
    synonyms: ["coffee", "cà phê", "ca phe", "robusta", "arabica"] },
  { hs6: "030617", covered: true,  name_en: "Frozen shrimp",  name_vi: "Tôm đông lạnh",
    synonyms: ["shrimp", "prawn", "tôm", "tom", "seafood", "thủy sản", "thuy san"] },
  { hs6: "080131", covered: true,  name_en: "Cashew (in shell)", name_vi: "Hạt điều",
    synonyms: ["cashew", "hạt điều", "hat dieu", "điều", "dieu", "nut"] },
  { hs6: "100630", covered: true,  name_en: "Milled rice",    name_vi: "Gạo",
    synonyms: ["rice", "gạo", "gao"] },
  { hs6: "TOTAL",  covered: true,  name_en: "All products",   name_vi: "Tất cả sản phẩm",
    synonyms: ["all", "total", "tất cả", "tat ca", "everything", "tổng"] },
  { hs6: "8517",   covered: true,  name_en: "Phones & telecom", name_vi: "Điện thoại & viễn thông",
    synonyms: ["phone", "smartphone", "điện thoại", "dien thoai", "telecom", "mobile"] },
  { hs6: "8542",   covered: true,  name_en: "Integrated circuits", name_vi: "Vi mạch (IC)",
    synonyms: ["chip", "ic", "integrated circuit", "vi mạch", "vi mach", "semiconductor", "chất bán dẫn"] },
  { hs6: "6109",   covered: true,  name_en: "T-shirts",       name_vi: "Áo thun",
    synonyms: ["t-shirt", "tshirt", "áo thun", "ao thun", "shirt", "dệt may", "garment"] },
  { hs6: "6110",   covered: true,  name_en: "Knitwear",       name_vi: "Áo len dệt kim",
    synonyms: ["sweater", "knitwear", "áo len", "ao len", "pullover"] },
  { hs6: "6403",   covered: true,  name_en: "Leather footwear", name_vi: "Giày da",
    synonyms: ["footwear", "shoes", "giày", "giay", "giày da", "leather shoes"] },
  { hs6: "9403",   covered: true,  name_en: "Furniture",      name_vi: "Đồ nội thất",
    synonyms: ["furniture", "đồ gỗ", "do go", "nội thất", "noi that", "đồ nội thất"] },
  { hs6: "4001",   covered: true,  name_en: "Natural rubber", name_vi: "Cao su tự nhiên",
    synonyms: ["rubber", "cao su", "natural rubber", "latex"] },
  { hs6: "0904",   covered: true,  name_en: "Pepper",         name_vi: "Hạt tiêu",
    synonyms: ["pepper", "tiêu", "tieu", "hạt tiêu", "hat tieu", "black pepper"] },
  { hs6: "0304",   covered: true,  name_en: "Fish fillets",   name_vi: "Phi lê cá",
    synonyms: ["fish", "cá", "ca", "fillet", "phi lê", "phi le", "pangasius", "cá tra"] },
  { hs6: "0803",   covered: true,  name_en: "Bananas",        name_vi: "Chuối",
    synonyms: ["banana", "chuối", "chuoi", "fruit"] },
  { hs6: "2709",   covered: true,  name_en: "Crude oil",      name_vi: "Dầu thô",
    synonyms: ["oil", "crude", "dầu thô", "dau tho", "petroleum", "dầu"] },
  { hs6: "8703",   covered: true,  name_en: "Cars",           name_vi: "Ô tô",
    synonyms: ["car", "ô tô", "o to", "vehicle", "automobile", "xe hơi"] },
  { hs6: "1201",   covered: true,  name_en: "Soybeans",       name_vi: "Đậu tương",
    synonyms: ["soybean", "soy", "đậu tương", "dau tuong", "đậu nành"] },
  { hs6: "1511",   covered: true,  name_en: "Palm oil",       name_vi: "Dầu cọ",
    synonyms: ["palm oil", "dầu cọ", "dau co", "palm"] },
];

const BY_HS = Object.fromEntries(CATALOG.map((c) => [c.hs6, c]));

export function lookup(hs6) {
  return BY_HS[hs6] || null;
}

// Lowercase + strip Vietnamese diacritics for forgiving matching ("trà" == "tra").
export function norm(s) {
  return (s || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/đ/g, "d"); // đ -> d
}

export function search(query, limit = 6) {
  const q = norm(query).trim();
  if (!q) return [];
  return CATALOG
    .map((c) => {
      const hay = [c.name_en, c.name_vi, ...c.synonyms].map(norm);
      const exact = hay.some((h) => h === q);
      const starts = hay.some((h) => h.startsWith(q));
      const has = hay.some((h) => h.includes(q));
      const score = exact ? 0 : starts ? 1 : has ? 2 : 99;
      return { c, score };
    })
    .filter((r) => r.score < 99)
    .sort((a, b) => a.score - b.score || (b.c.covered - a.c.covered))
    .slice(0, limit)
    .map((r) => r.c);
}
