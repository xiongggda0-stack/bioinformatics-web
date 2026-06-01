const displayDateFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "UTC"
});

export function formatDisplayDate(value) {
  return displayDateFormatter.format(new Date(value));
}
