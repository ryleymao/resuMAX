import { getMockDashboardData } from "./dashboard";
import type { ProfileData } from "@/app/profile/lib/profile";

export function getMockProfileData(): ProfileData {
  const mockResumes = getMockDashboardData().recentOptimizations.map((item, idx) => ({
    userId: "mock-user",
    resumeId: item.id || `mock-resume-${idx + 1}`,
    originalFileName: item.title,
    uploadedAt: item.updatedAt,
    optimizedAt: item.updatedAt,
    status: "optimized",
    relevanceScore: item.score,
  }));

  return {
    info: {
      name: "Mock User",
      email: "mock@example.com",
    },
    resumes: mockResumes,
  };
}
