import type { ResumeMetadata } from "@/lib/api";

export type ProfileInfo = {
  name?: string;
  email?: string;
};

export type ProfileData = {
  info: ProfileInfo;
  resumes: ResumeMetadata[];
};