export const PageInsights = ({ slug = "index", insights }) => {
  const entry = insights?.[slug];

  if (!entry || entry.pageKind !== "article") return null;

  const showReadingTime = !entry.hideReadingTime && typeof entry.readingMinutes === "number";
  const hint =
    entry.lengthBand === "long"
      ? "本文较长，建议先看摘要再按目录阅读。"
      : entry.lengthBand === "short"
        ? "本文内容较短，适合作为索引或补充说明。"
        : "";

  return (
    <section className="page-insights" data-length-band={entry.lengthBand}>
      {showReadingTime ? (
        <div className="page-insights-meta">预计阅读 {entry.readingMinutes} 分钟</div>
      ) : null}
      {!entry.hideSummary && entry.summary ? (
        <p className="page-insights-summary">{entry.summary}</p>
      ) : null}
      {hint ? <p className="page-insights-hint">{hint}</p> : null}
    </section>
  );
};
