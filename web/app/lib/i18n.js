/**
 * i18n.js — VN-default UI strings (plan §10.4: Vietnamese first, English second).
 * @context  Tiny hand table for the MVP. Grows into a real i18n lib when screens multiply.
 * @limits   Strings only.
 * @affects  page.js + components read via t(lang).
 */
const STRINGS = {
  vi: {
    tagline: "Ra-đa nhu cầu xuất khẩu",
    subtitle: "Nhu cầu thế giới đang dịch chuyển ở đâu — cho nhà xuất khẩu Việt Nam",
    product: "Sản phẩm",
    flowImport: "Nước nhập khẩu báo cáo",
    period: "Kỳ",
    published: "công bố",
    feedTitle: "Tín hiệu nhu cầu",
    feedNote: "Chỉ hiện tín hiệu từ mức “vừa” trở lên (±15%). Suy giảm cũng là tín hiệu.",
    marketsTitle: "Thị trường đích",
    vnShare: "Thị phần Việt Nam",
    yoy: "So cùng kỳ năm trước",
    sample: "DỮ LIỆU MẪU — chưa phải số liệu thật. Chỉ để minh hoạ giao diện.",
    noData: "Chưa có dữ liệu. Chạy ETL: cd etl && python -m tradepulse_etl",
    lang: "English",
    disclaimer: "Thông tin, không phải tư vấn. Nguồn chính thức là căn cứ cuối cùng. Số liệu thương mại có độ trễ.",
    noSignal: "Chưa đủ dữ liệu cho tín hiệu",
  },
  en: {
    tagline: "Export demand radar",
    subtitle: "Where world demand is moving — for Vietnamese exporters",
    product: "Product",
    flowImport: "Importer-reported",
    period: "Period",
    published: "published",
    feedTitle: "Demand signals",
    feedNote: "Shows moderate+ only (±15%). Declines are signals too.",
    marketsTitle: "Destination markets",
    vnShare: "Vietnam share",
    yoy: "Year-over-year",
    sample: "SAMPLE DATA — not real figures. For UI demonstration only.",
    noData: "No data yet. Run the ETL: cd etl && python -m tradepulse_etl",
    lang: "Tiếng Việt",
    disclaimer: "Information, not advice. Official sources govern. Trade data lags.",
    noSignal: "Not enough data for a signal",
  },
};

export function t(lang) {
  return STRINGS[lang === "en" ? "en" : "vi"];
}
