# API Registry - ResuMAX

Complete API documentation for all endpoints.

---

## Authentication

All endpoints require Firebase authentication unless noted.

**Header**: `Authorization: Bearer <firebase_token>`

---

## Upload

### Upload Resume
- **POST** `/api/upload`
- **Auth**: Required
- **Body**: `multipart/form-data`
  - `file`: PDF, DOCX, or TXT file
- **Response**:
  ```json
  {
    "resume_id": "uuid",
    "user_id": "firebase_uid",
    "name": "filename.pdf",
    "data": {
      "header": {...},
      "experience": [...],
      "projects": [...],
      "skills": {...},
      "education": [...]
    },
    "created_at": "2024-12-02T...",
    "updated_at": "2024-12-02T..."
  }
  ```
- **Description**: Uploads and parses resume using GPT-4 LLM
- **Cost**: ~$0.01 per upload

---

## Resumes (CRUD)

### List Resumes
- **GET** `/api/resume`
- **Auth**: Required
- **Response**: `Array<ResumeResponse>`
- **Description**: Returns all resumes for current user

### Get Resume
- **GET** `/api/resume/{resume_id}`
- **Auth**: Required
- **Response**: `ResumeResponse`
- **Description**: Get specific resume by ID

### Update Resume
- **PUT** `/api/resume/{resume_id}`
- **Auth**: Required
- **Body**:
  ```json
  {
    "data": {
      "header": {...},
      "summary": "...",
      "experience": [...],
      "projects": [...],
      "skills": {...},
      "education": [...]
    }
  }
  ```
- **Response**: `ResumeResponse`
- **Description**: Update resume content

### Delete Resume
- **DELETE** `/api/resume/{resume_id}`
- **Auth**: Required
- **Response**: `{"message": "Resume deleted successfully"}`
- **Description**: Permanently delete resume

---

## Job Analysis ✨ NEW

### Analyze Job Description
- **POST** `/api/job/analyze`
- **Auth**: Required
- **Body**:
  ```json
  {
    "job_description": "Senior Software Engineer...",
    "resume_id": "optional-uuid"
  }
  ```
- **Response**:
  ```json
  {
    "job_analysis": {
      "required_keywords": ["Python", "React", "AWS"],
      "preferred_keywords": ["Docker", "Kubernetes"],
      "missing_skills": [],
      "role_level": "Senior",
      "industry": "Technology",
      "key_responsibilities": [
        "Lead engineering team",
        "Design scalable systems"
      ]
    },
    "gap_analysis": {
      "missing_keywords": ["Kubernetes", "GraphQL"],
      "weak_bullets": [
        {
          "bullet_text": "Managed projects",
          "reason": "Lacks metrics and specifics",
          "suggestion": "Led 5+ cross-functional projects..."
        }
      ],
      "alignment_score": 72.5,
      "recommendations": [
        "Add quantifiable metrics to bullets",
        "Include Kubernetes experience",
        "Highlight leadership experience"
      ]
    }
  }
  ```
- **Description**: Analyzes job description using GPT-4o-mini. If `resume_id` provided, also performs gap analysis.
- **Cost**: ~$0.001 per call
- **Use Cases**:
  - Extract keywords from JD
  - Identify missing skills
  - Find weak bullets to improve
  - Calculate resume-job alignment

---

## Optimization

### Optimize Single Bullet
- **POST** `/api/optimize/bullet`
- **Auth**: Required
- **Body**:
  ```json
  {
    "bullet": "Managed team projects",
    "context": {
      "job_title": "Senior Engineer",
      "company": "Tech Corp"
    }
  }
  ```
- **Response**:
  ```json
  {
    "optimized": "Led cross-functional team of 5 engineers on 3 high-impact projects, reducing delivery time by 30%"
  }
  ```
- **Description**: Uses GPT-4 to rewrite bullet with metrics and action verbs
- **Cost**: ~$0.005 per bullet

---

## Export

### Export PDF
- **POST** `/api/export/pdf`
- **Auth**: Required
- **Body**:
  ```json
  {
    "resume_id": "uuid",
    "format": "pdf",
    "options": {
      "font_family": "Helvetica",
      "font_size": 10,
      "theme": "professional"
    }
  }
  ```
- **Response**: Binary PDF file
- **Headers**: `Content-Disposition: attachment; filename="resume_optimized.pdf"`
- **Description**: Generates professional one-page PDF using ReportLab
- **Font Options**: `Helvetica`, `Times`, `Courier`
- **Size Options**: `8`-`12` (points)
- **Theme Options**: `professional`, `modern`, `minimal`

---

## Health Check

### Root
- **GET** `/`
- **Auth**: Not required
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "ResuMAX API",
    "version": "1.0.0"
  }
  ```

### Detailed Health
- **GET** `/health`
- **Auth**: Not required
- **Response**:
  ```json
  {
    "status": "healthy",
    "environment": "development",
    "firebase": "connected"
  }
  ```

---

## Error Responses

All endpoints follow standard HTTP error codes:

### 400 Bad Request
```json
{
  "detail": "Invalid file type. Allowed: .pdf, .docx, .txt"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resume not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to parse resume: <error message>"
}
```

---

## Cost Summary

| Endpoint | Model | Typical Cost |
|----------|-------|--------------|
| `/api/upload` | GPT-4 Turbo | ~$0.01 |
| `/api/job/analyze` | GPT-4o-mini | ~$0.001 |
| `/api/optimize/bullet` | GPT-4 | ~$0.005 |
| `/api/export/pdf` | None (ReportLab) | $0 |

**Typical user flow**: Upload + Analyze JD + Optimize 5 bullets = **~$0.036**

---

**Last Updated**: December 2024 (Updated with full optimization endpoint and improved error handling)
