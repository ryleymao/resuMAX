import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Underline } from '@tiptap/extension-underline';
import { TextAlign } from '@tiptap/extension-text-align';
import { Color } from '@tiptap/extension-color';
import { TextStyle } from '@tiptap/extension-text-style';
import { FontFamily } from '@tiptap/extension-font-family';
import { useEffect, useRef, useState } from 'react';
import { Resume } from '../types/resume';

interface UnifiedResumeEditorProps {
  resume: Resume;
  onChange: (html: string) => void;
}

// Convert structured resume data to HTML
function resumeToHTML(resume: Resume): string {
  let html = '';

  // Header
  html += `<h1 style="text-align: center;">${resume.header.name || 'Your Name'}</h1>`;

  // Contact info
  if (resume.header.contact) {
    const contact = resume.header.contact;
    const contactItems = [];
    if (contact.email) contactItems.push(contact.email);
    if (contact.phone) contactItems.push(contact.phone);
    if (contact.location) contactItems.push(contact.location);
    if (contact.linkedin) contactItems.push(contact.linkedin);
    if (contact.github) contactItems.push(contact.github);
    if (contact.website) contactItems.push(contact.website);

    if (contactItems.length > 0) {
      html += `<p style="text-align: center;">${contactItems.join(' • ')}</p>`;
    }
  }

  html += '<hr>';

  // Summary
  if (resume.summary) {
    html += `<h2>Professional Summary</h2>`;
    html += `<p>${resume.summary}</p>`;
  }

  // Experience
  if (resume.experience && resume.experience.length > 0) {
    html += `<h2>Experience</h2>`;

    resume.experience.forEach(exp => {
      // Company and Location on first line
      html += `<p style="display: flex; justify-content: space-between;"><strong>${exp.company}</strong><span>${exp.location || ''}</span></p>`;
      // Title and Dates on second line
      html += `<p style="display: flex; justify-content: space-between;">${exp.title}<span>${exp.start_date} - ${exp.end_date || 'Present'}</span></p>`;

      if (exp.bullets && exp.bullets.length > 0) {
        html += '<ul>';
        exp.bullets.forEach(bullet => {
          html += `<li>${bullet}</li>`;
        });
        html += '</ul>';
      }

      if (exp.technologies && exp.technologies.length > 0) {
        html += `<p><em>Technologies: ${exp.technologies.join(', ')}</em></p>`;
      }
    });
  }

  // Projects
  if (resume.projects && resume.projects.length > 0) {
    html += `<h2>Projects</h2>`;

    resume.projects.forEach(project => {
      html += `<p><strong>${project.name}</strong></p>`;
      if (project.description) {
        html += `<p>${project.description}</p>`;
      }

      if (project.bullets && project.bullets.length > 0) {
        html += '<ul>';
        project.bullets.forEach(bullet => {
          html += `<li>${bullet}</li>`;
        });
        html += '</ul>';
      }

      if (project.technologies && project.technologies.length > 0) {
        html += `<p><em>Technologies: ${project.technologies.join(', ')}</em></p>`;
      }
    });
  }

  // Skills
  if (resume.skills && Object.keys(resume.skills).length > 0) {
    html += `<h2>Skills</h2>`;

    Object.entries(resume.skills).forEach(([category, skills]) => {
      html += `<p><strong>${category}:</strong> ${skills.join(', ')}</p>`;
    });
  }

  // Education
  if (resume.education && resume.education.length > 0) {
    html += `<h2>Education</h2>`;

    resume.education.forEach(edu => {
      html += `<p style="display: flex; justify-content: space-between;"><strong>${edu.degree}${edu.field ? ' in ' + edu.field : ''}</strong><span>${edu.institution}</span></p>`;
      html += `<p>${edu.end_date || edu.start_date}${edu.location ? ' • ' + edu.location : ''}</p>`;

      if (edu.gpa) {
        html += `<p>GPA: ${edu.gpa}</p>`;
      }
    });
  }

  return html;
}

export function UnifiedResumeEditor({ resume, onChange }: UnifiedResumeEditorProps) {
  const pageRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);
  const [scale, setScale] = useState(0.85);
  const [compressionLevel, setCompressionLevel] = useState(0); // 0-4 levels of compression

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Underline,
      TextStyle,
      Color,
      FontFamily,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
    ],
    content: resumeToHTML(resume),
    editorProps: {
      handleKeyDown: (view, event) => {
        if (event.key === 'Tab') {
          event.preventDefault();
          view.dispatch(view.state.tr.insertText('    '));
          return true;
        }
        return false;
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
      // Check for overflow after content changes
      setTimeout(() => checkOverflow(), 100);
    },
  });

  // Update content when resume changes (e.g., after optimization)
  useEffect(() => {
    if (editor && resume) {
      const newHTML = resumeToHTML(resume);
      if (editor.getHTML() !== newHTML) {
        editor.commands.setContent(newHTML);
      }
    }
  }, [resume, editor]);

  // Check if content exceeds one page (without auto-compression to prevent loops)
  const checkOverflow = () => {
    if (!pageRef.current) return;

    const isContentOverflowing = pageRef.current.scrollHeight > pageRef.current.clientHeight;
    setIsOverflowing(isContentOverflowing);
  };

  // Check overflow after initial render and editor updates
  useEffect(() => {
    if (editor) {
      const timer = setTimeout(() => checkOverflow(), 200);
      return () => clearTimeout(timer);
    }
  }, [editor, resume, compressionLevel]);

  if (!editor) {
    return null;
  }

  // Calculate compression CSS values based on level
  const getCompressionStyles = () => {
    const baseLineHeight = 1.2;
    const baseFontSize = 10;
    const baseLetterSpacing = 0;
    const baseBulletIndent = 18;
    const baseSectionMargin = 8;
    const baseParagraphMargin = 3;
    const baseBulletMargin = 1;

    switch (compressionLevel) {
      case 1: // Reduce line-height
        return {
          lineHeight: 1.15,
          fontSize: baseFontSize,
          letterSpacing: baseLetterSpacing,
          bulletIndent: baseBulletIndent,
          sectionMargin: baseSectionMargin,
          paragraphMargin: baseParagraphMargin,
          bulletMargin: baseBulletMargin,
        };
      case 2: // Tighten letter spacing
        return {
          lineHeight: 1.1,
          fontSize: baseFontSize,
          letterSpacing: -0.1,
          bulletIndent: baseBulletIndent,
          sectionMargin: baseSectionMargin,
          paragraphMargin: baseParagraphMargin,
          bulletMargin: baseBulletMargin,
        };
      case 3: // Reduce vertical spacing
        return {
          lineHeight: 1.1,
          fontSize: baseFontSize,
          letterSpacing: -0.1,
          bulletIndent: 15,
          sectionMargin: 6,
          paragraphMargin: 2,
          bulletMargin: 0.5,
        };
      case 4: // Reduce font size
        return {
          lineHeight: 1.1,
          fontSize: 9.5,
          letterSpacing: -0.1,
          bulletIndent: 15,
          sectionMargin: 5,
          paragraphMargin: 2,
          bulletMargin: 0.5,
        };
      default: // No compression
        return {
          lineHeight: baseLineHeight,
          fontSize: baseFontSize,
          letterSpacing: baseLetterSpacing,
          bulletIndent: baseBulletIndent,
          sectionMargin: baseSectionMargin,
          paragraphMargin: baseParagraphMargin,
          bulletMargin: baseBulletMargin,
        };
    }
  };

  const compressionStyles = getCompressionStyles();

  return (
    <div className="flex flex-col items-center">
      {/* Overflow Warning */}
      {isOverflowing && (
        <div className="mb-4 px-4 py-2 bg-red-50 border border-red-300 text-red-700 rounded-md text-sm flex items-center gap-3">
          <span>⚠️ Content exceeds one page.</span>
          <button
            onClick={() => setCompressionLevel(prev => Math.min(4, prev + 1))}
            className="px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
            disabled={compressionLevel >= 4}
          >
            Compress More
          </button>
        </div>
      )}

      {/* Controls */}
      <div className="mb-2 flex items-center gap-4 text-sm text-gray-600">
        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <span className="text-xs">Zoom:</span>
          <button
            onClick={() => setScale(Math.min(1.0, scale + 0.05))}
            className="px-2 py-1 border rounded hover:bg-gray-50"
          >
            +
          </button>
          <span>{Math.round(scale * 100)}%</span>
          <button
            onClick={() => setScale(Math.max(0.5, scale - 0.05))}
            className="px-2 py-1 border rounded hover:bg-gray-50"
          >
            -
          </button>
        </div>

        {/* Compression Controls */}
        <div className="flex items-center gap-2">
          <span className="text-xs">Compression:</span>
          <button
            onClick={() => setCompressionLevel(prev => Math.max(0, prev - 1))}
            className="px-2 py-1 border rounded hover:bg-gray-50"
            disabled={compressionLevel <= 0}
          >
            -
          </button>
          <span className={compressionLevel > 0 ? 'text-orange-600 font-medium' : ''}>
            {compressionLevel}/4
          </span>
          <button
            onClick={() => setCompressionLevel(prev => Math.min(4, prev + 1))}
            className="px-2 py-1 border rounded hover:bg-gray-50"
            disabled={compressionLevel >= 4}
          >
            +
          </button>
        </div>
      </div>

      {/* Scale Wrapper - scales entire page for preview */}
      <div
        className="scale-wrapper"
        style={{
          '--ui-scale': scale,
          transform: `scale(${scale})`,
          transformOrigin: 'top center',
          marginBottom: `${(1 - scale) * 500}px` // Adjust bottom spacing based on scale
        } as React.CSSProperties}
      >
        {/* Fixed Page Container - 8.5" x 11" (816px x 1056px) */}
        <div
          className="bg-white shadow-lg"
          style={{
            width: '816px',   // 8.5in * 96px/in
            height: '1056px', // 11in * 96px/in
            border: '1px solid #ccc',
            boxShadow: '0 0 8px rgba(0,0,0,0.15)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden', // DO NOT ALLOW SCROLLING
            position: 'relative'
          }}
        >
          {/* Formatting Toolbar */}
          <div className="border-b border-gray-200 p-2 flex flex-wrap gap-2 bg-white" style={{ flexShrink: 0 }}>
            <button
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive('bold') ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              <strong>B</strong>
            </button>
            <button
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive('italic') ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              <em>I</em>
            </button>
            <button
              onClick={() => editor.chain().focus().toggleUnderline().run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive('underline') ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              <u>U</u>
            </button>

            <div className="w-px h-6 bg-gray-300 mx-1"></div>

            <button
              onClick={() => editor.chain().focus().setTextAlign('left').run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive({ textAlign: 'left' }) ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              Left
            </button>
            <button
              onClick={() => editor.chain().focus().setTextAlign('center').run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive({ textAlign: 'center' }) ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              Center
            </button>
            <button
              onClick={() => editor.chain().focus().setTextAlign('right').run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive({ textAlign: 'right' }) ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              Right
            </button>

            <div className="w-px h-6 bg-gray-300 mx-1"></div>

            <button
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive('bulletList') ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              • List
            </button>
            <button
              onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
              className={`px-3 py-1 text-sm border rounded ${editor.isActive('heading', { level: 2 }) ? 'bg-blue-100 border-blue-300' : 'border-gray-300'}`}
            >
              H2
            </button>
          </div>

          {/* Page Content - Fixed Height with Overflow Detection */}
          <div
            ref={pageRef}
            style={{
              flex: 1,
              overflow: 'hidden', // CRITICAL: No scrolling allowed
              position: 'relative'
            }}
          >
            <style>{`
              /* Enable hyphenation globally */
              .resume-page-editor .ProseMirror {
                padding: 48px; /* 0.5in margins */
                height: 100%;
                outline: none;
                font-family: 'Arial', sans-serif;
                font-size: ${compressionStyles.fontSize}pt;
                line-height: ${compressionStyles.lineHeight};
                letter-spacing: ${compressionStyles.letterSpacing}px;
                color: #000;
                overflow: hidden;

                /* Hyphenation and word breaking */
                hyphens: auto;
                -webkit-hyphens: auto;
                -moz-hyphens: auto;
                -ms-hyphens: auto;
                overflow-wrap: break-word;
                word-break: normal;
                hyphenate-limit-chars: 6 3 2;
                hyphenate-limit-lines: 2;
                hyphenate-limit-zone: 8%;
              }

              .resume-page-editor .ProseMirror h1 {
                font-size: 14pt;
                font-weight: bold;
                margin: 0 0 4pt 0;
                line-height: 1.0;
                hyphens: none; /* Don't hyphenate headings */
              }

              .resume-page-editor .ProseMirror h2 {
                font-size: 11pt;
                font-weight: bold;
                margin: ${compressionStyles.sectionMargin}pt 0 3pt 0;
                line-height: 1.0;
                hyphens: none; /* Don't hyphenate headings */
              }

              .resume-page-editor .ProseMirror p {
                margin: 0 0 ${compressionStyles.paragraphMargin}pt 0;
                line-height: ${compressionStyles.lineHeight};
              }

              .resume-page-editor .ProseMirror ul {
                margin: 2pt 0;
                padding-left: ${compressionStyles.bulletIndent}pt;
              }

              .resume-page-editor .ProseMirror li {
                margin: 0 0 ${compressionStyles.bulletMargin}pt 0;
                line-height: ${compressionStyles.lineHeight};
              }

              .resume-page-editor .ProseMirror hr {
                border: none;
                border-top: 1px solid #ccc;
                margin: 4pt 0;
              }
            `}</style>
            <div className="resume-page-editor" ref={contentRef}>
              <EditorContent editor={editor} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
