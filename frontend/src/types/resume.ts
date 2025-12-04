export interface ContactInfo {
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  github?: string
  website?: string
  other?: Record<string, string>
}

export interface ExperienceItem {
  company: string
  title: string
  location?: string
  start_date: string
  end_date?: string
  current: boolean
  bullets: string[]
  technologies: string[]
}

export interface ProjectItem {
  name: string
  description?: string
  url?: string
  start_date?: string
  end_date?: string
  bullets: string[]
  technologies: string[]
}

export interface EducationItem {
  institution: string
  degree: string
  field?: string
  location?: string
  start_date?: string
  end_date?: string
  gpa?: string
  honors: string[]
  coursework: string[]
}

export interface CertificationItem {
  name: string
  issuer?: string
  date?: string
  expiry?: string
  credential_id?: string
  url?: string
}

export interface AwardItem {
  name: string
  issuer?: string
  date?: string
  description?: string
}

export interface FormattingMetadata {
  font_family?: string
  font_size?: number
  is_bold?: boolean
  is_italic?: boolean
  spacing_before?: number
  spacing_after?: number
  alignment?: string
}

export interface FlexibleSection {
  title: string  // Original section title
  type: string   // volunteer, publications, languages, etc.
  content: any   // Flexible content
  formatting?: FormattingMetadata
  order: number
}

export interface Resume {
  header: {
    name: string
    title: string
    contact: ContactInfo
  }
  summary: string

  // Standard sections
  experience: ExperienceItem[]
  projects: ProjectItem[]
  skills: Record<string, string[]>
  education: EducationItem[]

  // New sections
  certifications: CertificationItem[]
  awards: AwardItem[]
  flexible_sections: FlexibleSection[]

  // Formatting
  formatting?: FormattingMetadata

  // Legacy
  extra: Record<string, any>
}

export interface ResumeResponse {
  resume_id: string
  user_id: string
  name: string
  data: Resume
  target_job_intelligence_id?: string
  created_at: string
  updated_at: string
}

export interface JobIntelligence {
  role: string
  seniority: string
  top_skills_required: string[]
  must_have_keywords: string[]
  nice_to_haves: string[]
  core_responsibilities: string[]
  attributes_recruiters_care_about: string[]
}

export interface JobIntelligenceResponse {
  job_intelligence_id: string
  user_id: string
  data: JobIntelligence
  source_url?: string
  company_name?: string
  created_at: string
}
