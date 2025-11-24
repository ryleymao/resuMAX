import Link from "next/link";

const items = [
  { label: "Overview", href: "#overview" },
  { label: "Experience", href: "#experience" },
  { label: "Projects", href: "#projects" },
  { label: "Skills", href: "#skills" },
  { label: "Education", href: "#education" },
  { label: "Sources", href: "#sources" },
];

export function ProfileSidebar() {
  return (
    <nav className="space-y-2 text-sm text-white/80">
      {items.map((item) => (
        <Link key={item.href} href={item.href} className="block rounded-lg px-3 py-2 hover:bg-white/10">
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
