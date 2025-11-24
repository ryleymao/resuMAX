export type OptimizationItem = {
  id: string;
  title: string;
  updatedAt: string;
  score: number;
};

export type RecentJob = {
  id: string;
  title: string;
  addedAt: string;
};

export type DashboardData = {
  lastUpload: {
    date: string;
    status: "parsed" | "not_parsed";
  };
  profileSnapshot: {
    experiences: number;
    skills: number;
    projects: number;
  };
  recentJobs: RecentJob[];
  recentOptimizations: OptimizationItem[];
};
