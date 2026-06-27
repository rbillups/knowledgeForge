export function getCitationDisclosureLabel(count: number): string {
  if (count === 1) {
    return "View supporting source";
  }

  return `View ${count} supporting sources`;
}
