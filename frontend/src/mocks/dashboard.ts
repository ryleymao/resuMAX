import type { DashboardData } from "@/app/dashboard/lib/dashboard";

export function getMockDashboardData(): DashboardData {
  return {
    lastUpload: {
      date: "2025-11-10",
      status: "parsed",
    },
    profileSnapshot: {
      experiences: 6,
      skills: 14,
      projects: 4,
    },
    recentJobs: [
      { id: "job-1", title: "Senior Product Manager", addedAt: "2025-11-20" },
      { id: "job-2", title: "Lead Data Analyst", addedAt: "2025-11-18" },
      { id: "job-3", title: "Staff Software Engineer", addedAt: "2025-11-15" },
    ],
    recentOptimizations: [
      { id: "opt-1", title: "PM Resume - fintech focus", updatedAt: "2025-11-22", score: 92 },
      { id: "opt-2", title: "Data Analyst - enterprise SaaS", updatedAt: "2025-11-20", score: 87 },
      { id: "opt-3", title: "Backend SWE - platform team", updatedAt: "2025-11-18", score: 90 },
    ],
  };
}
