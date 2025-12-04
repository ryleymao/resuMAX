import { Resume } from '../types/resume'

interface ResumePreviewProps {
  resume: Resume
  fontFamily?: string
  fontSize?: number
  theme?: string
}

export default function ResumePreview({
  resume,
  fontFamily = 'Helvetica',
  fontSize = 10,
  theme = 'professional'
}: ResumePreviewProps) {

  // Theme colors
  const themes = {
    professional: { primary: '#1e40af', secondary: '#3b82f6', text: '#1f2937' },
    modern: { primary: '#7c3aed', secondary: '#a78bfa', text: '#1f2937' },
    minimal: { primary: '#000000', secondary: '#374151', text: '#1f2937' }
  }

  const colors = themes[theme as keyof typeof themes] || themes.professional

  // Base font size in pixels (converted from pt)
  const baseFontSize = fontSize * 1.33 // 1pt = 1.33px

  const styles = {
    container: {
      fontFamily: fontFamily,
      fontSize: `${baseFontSize}px`,
      lineHeight: '1.4',
      color: colors.text,
      // EXACT PDF dimensions: 8.5" x 11" with 0.5" margins
      width: '8.5in',
      height: '11in',
      margin: '0 auto',
      padding: '0.5in',
      backgroundColor: 'white',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      // Ensure pixel-perfect rendering
      boxSizing: 'border-box' as const,
      overflow: 'hidden',  // Enforce one-page limit
      position: 'relative' as const
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: `${baseFontSize * 0.6}px`,
      paddingBottom: `${baseFontSize * 0.4}px`,
      borderBottom: `2px solid ${colors.primary}`
    },
    name: {
      fontSize: `${baseFontSize * 2}px`,
      fontWeight: 'bold',
      color: colors.primary,
      marginBottom: `${baseFontSize * 0.3}px`
    },
    title: {
      fontSize: `${baseFontSize * 1.2}px`,
      color: colors.secondary,
      marginBottom: `${baseFontSize * 0.4}px`
    },
    contact: {
      fontSize: `${baseFontSize * 0.9}px`,
      color: colors.text,
      display: 'flex',
      justifyContent: 'center',
      gap: `${baseFontSize * 0.5}px`,
      flexWrap: 'wrap' as const
    },
    sectionHeader: {
      fontSize: `${baseFontSize * 1.3}px`,
      fontWeight: 'bold',
      color: colors.primary,
      borderBottom: `1px solid ${colors.secondary}`,
      marginTop: `${baseFontSize * 0.5}px`,
      marginBottom: `${baseFontSize * 0.4}px`,
      paddingBottom: `${baseFontSize * 0.1}px`,
      textTransform: 'uppercase' as const,
      letterSpacing: '0.5px'
    },
    experienceItem: {
      marginBottom: `${baseFontSize * 0.5}px`
    },
    jobHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      marginBottom: `${baseFontSize * 0.2}px`
    },
    jobTitle: {
      fontWeight: 'bold',
      fontSize: `${baseFontSize * 1.1}px`
    },
    company: {
      color: colors.secondary,
      fontSize: `${baseFontSize * 1}px`
    },
    dateLocation: {
      fontSize: `${baseFontSize * 0.9}px`,
      color: '#6b7280',
      fontStyle: 'italic' as const
    },
    bullet: {
      marginLeft: `${baseFontSize * 1}px`,
      marginBottom: `${baseFontSize * 0.3}px`,
      fontSize: `${baseFontSize}px`,
      lineHeight: '1.4'
    },
    skillCategory: {
      marginBottom: `${baseFontSize * 0.5}px`
    },
    skillLabel: {
      fontWeight: 'bold',
      display: 'inline',
      marginRight: `${baseFontSize * 0.3}px`
    }
  }

  const renderContact = () => {
    const { contact } = resume.header
    const items = []

    if (contact?.email) items.push(contact.email)
    if (contact?.phone) items.push(contact.phone)
    if (contact?.location) items.push(contact.location)
    if (contact?.linkedin) items.push(contact.linkedin)
    if (contact?.github) items.push(contact.github)
    if (contact?.website) items.push(contact.website)

    return items.join(' • ')
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.name}>{resume.header.name}</div>
        {resume.header.title && <div style={styles.title}>{resume.header.title}</div>}
        {resume.header.contact && (
          <div style={styles.contact}>
            {renderContact()}
          </div>
        )}
      </div>

      {/* Summary */}
      {resume.summary && (
        <div style={{ marginBottom: `${baseFontSize * 0.4}px` }}>
          <div style={styles.sectionHeader}>Professional Summary</div>
          <div
            style={{ margin: 0, lineHeight: '1.4' }}
            dangerouslySetInnerHTML={{ __html: resume.summary }}
          />
        </div>
      )}

      {/* Experience */}
      {resume.experience && resume.experience.length > 0 && (
        <div>
          <div style={styles.sectionHeader}>Experience</div>
          {resume.experience.map((exp, idx) => (
            <div key={idx} style={styles.experienceItem}>
              <div style={styles.jobHeader}>
                <div>
                  <span style={styles.jobTitle}>{exp.title}</span>
                  {' • '}
                  <span style={styles.company}>{exp.company}</span>
                </div>
                <div style={styles.dateLocation}>
                  {exp.start_date} - {exp.end_date || 'Present'}
                  {exp.location && ` • ${exp.location}`}
                </div>
              </div>
              {exp.bullets && exp.bullets.length > 0 && (
                <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                  {exp.bullets.map((bullet, bidx) => (
                    <li key={bidx} style={styles.bullet}>
                      <span dangerouslySetInnerHTML={{ __html: `• ${bullet}` }} />
                    </li>
                  ))}
                </ul>
              )}
              {exp.technologies && exp.technologies.length > 0 && (
                <div style={{ marginTop: `${baseFontSize * 0.3}px`, fontSize: `${baseFontSize * 0.9}px`, fontStyle: 'italic', color: '#6b7280' }}>
                  <strong>Technologies:</strong> {exp.technologies.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Projects */}
      {resume.projects && resume.projects.length > 0 && (
        <div>
          <div style={styles.sectionHeader}>Projects</div>
          {resume.projects.map((project, idx) => (
            <div key={idx} style={styles.experienceItem}>
              <div style={styles.jobHeader}>
                <div>
                  <span style={styles.jobTitle}>{project.name}</span>
                  {project.url && (
                    <span style={{ fontSize: `${baseFontSize * 0.9}px`, marginLeft: `${baseFontSize * 0.3}px` }}>
                      ({project.url})
                    </span>
                  )}
                </div>
                {(project.start_date || project.end_date) && (
                  <div style={styles.dateLocation}>
                    {project.start_date} {project.end_date && `- ${project.end_date}`}
                  </div>
                )}
              </div>
              {project.description && (
                <p style={{ margin: `${baseFontSize * 0.2}px 0`, fontStyle: 'italic' }}>{project.description}</p>
              )}
              {project.bullets && project.bullets.length > 0 && (
                <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                  {project.bullets.map((bullet, bidx) => (
                    <li key={bidx} style={styles.bullet}>
                      <span dangerouslySetInnerHTML={{ __html: `• ${bullet}` }} />
                    </li>
                  ))}
                </ul>
              )}
              {project.technologies && project.technologies.length > 0 && (
                <div style={{ marginTop: `${baseFontSize * 0.3}px`, fontSize: `${baseFontSize * 0.9}px`, fontStyle: 'italic', color: '#6b7280' }}>
                  <strong>Technologies:</strong> {project.technologies.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Education */}
      {resume.education && resume.education.length > 0 && (
        <div>
          <div style={styles.sectionHeader}>Education</div>
          {resume.education.map((edu, idx) => (
            <div key={idx} style={styles.experienceItem}>
              <div style={styles.jobHeader}>
                <div>
                  <span style={styles.jobTitle}>{edu.degree}</span>
                  {edu.field && <span> in {edu.field}</span>}
                  {' • '}
                  <span style={styles.company}>{edu.institution}</span>
                </div>
                <div style={styles.dateLocation}>
                  {edu.end_date || edu.start_date}
                  {edu.location && ` • ${edu.location}`}
                </div>
              </div>
              {edu.gpa && (
                <div style={{ fontSize: `${baseFontSize * 0.95}px` }}>GPA: {edu.gpa}</div>
              )}
              {edu.honors && edu.honors.length > 0 && (
                <div style={{ fontSize: `${baseFontSize * 0.95}px` }}>
                  <strong>Honors:</strong> {edu.honors.join(', ')}
                </div>
              )}
              {edu.coursework && edu.coursework.length > 0 && (
                <div style={{ fontSize: `${baseFontSize * 0.95}px` }}>
                  <strong>Relevant Coursework:</strong> {edu.coursework.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Skills */}
      {resume.skills && Object.keys(resume.skills).length > 0 && (
        <div>
          <div style={styles.sectionHeader}>Skills</div>
          {Object.entries(resume.skills).map(([category, skills], idx) => (
            <div key={idx} style={styles.skillCategory}>
              <span style={styles.skillLabel}>{category}:</span>
              <span>{skills.join(', ')}</span>
            </div>
          ))}
        </div>
      )}

      {/* Certifications */}
      {resume.certifications && resume.certifications.length > 0 && (
        <div>
          <div style={styles.sectionHeader}>Certifications</div>
          {resume.certifications.map((cert, idx) => (
            <div key={idx} style={styles.experienceItem}>
              <div style={styles.jobHeader}>
                <div>
                  <span style={styles.jobTitle}>{cert.name}</span>
                  {cert.issuer && (
                    <>
                      {' • '}
                      <span style={styles.company}>{cert.issuer}</span>
                    </>
                  )}
                </div>
                {cert.date && (
                  <div style={styles.dateLocation}>
                    {cert.date}
                    {cert.expiry && ` - ${cert.expiry}`}
                  </div>
                )}
              </div>
              {cert.credential_id && (
                <div style={{ fontSize: `${baseFontSize * 0.9}px`, color: '#6b7280' }}>
                  ID: {cert.credential_id}
                </div>
              )}
              {cert.url && (
                <div style={{ fontSize: `${baseFontSize * 0.9}px`, color: colors.secondary }}>
                  {cert.url}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Awards */}
      {resume.awards && resume.awards.length > 0 && (
        <div>
          <div style={styles.sectionHeader}>Awards & Honors</div>
          {resume.awards.map((award, idx) => (
            <div key={idx} style={styles.experienceItem}>
              <div style={styles.jobHeader}>
                <div>
                  <span style={styles.jobTitle}>{award.name}</span>
                  {award.issuer && (
                    <>
                      {' • '}
                      <span style={styles.company}>{award.issuer}</span>
                    </>
                  )}
                </div>
                {award.date && <div style={styles.dateLocation}>{award.date}</div>}
              </div>
              {award.description && (
                <p style={{ margin: 0, fontSize: `${baseFontSize * 0.95}px` }}>{award.description}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Flexible Sections */}
      {resume.flexible_sections && resume.flexible_sections.length > 0 && (
        <>
          {resume.flexible_sections
            .sort((a, b) => a.order - b.order)
            .map((section, idx) => (
              <div key={idx}>
                <div style={styles.sectionHeader}>{section.title}</div>
                <div style={{ marginBottom: `${baseFontSize * 0.8}px` }}>
                  {Array.isArray(section.content) ? (
                    <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                      {section.content.map((item: any, itemIdx: number) => (
                        <li key={itemIdx} style={styles.bullet}>
                          {typeof item === 'string' ? (
                            <>• {item}</>
                          ) : typeof item === 'object' ? (
                            <div>
                              {item.name && <span style={styles.jobTitle}>{item.name}</span>}
                              {item.title && <span style={styles.jobTitle}>{item.title}</span>}
                              {item.description && <div>{item.description}</div>}
                              {item.date && <span style={styles.dateLocation}> • {item.date}</span>}
                            </div>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  ) : typeof section.content === 'object' ? (
                    <div>
                      {Object.entries(section.content).map(([key, value]: [string, any], entryIdx) => (
                        <div key={entryIdx} style={styles.skillCategory}>
                          <span style={styles.skillLabel}>{key}:</span>
                          <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ margin: 0 }}>{String(section.content)}</p>
                  )}
                </div>
              </div>
            ))}
        </>
      )}
    </div>
  )
}
