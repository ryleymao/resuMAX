/**
 * Job Description Sidebar
 * Paste JD, analyze keywords, show gaps
 */
import { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface JobAnalysis {
    required_keywords: string[];
    preferred_keywords: string[];
    role_level: string;
    industry: string;
    key_responsibilities: string[];
}

interface GapAnalysis {
    missing_keywords: string[];
    weak_bullets: Array<{
        bullet_text: string;
        reason: string;
        suggestion: string;
    }>;
    alignment_score: number;
    recommendations: string[];
}

interface JobDescriptionSidebarProps {
    resumeId?: string;
    onKeywordsExtracted?: (keywords: string[]) => void;
    jobDescription: string;
    onJobDescriptionChange: (jd: string) => void;
}

export function JobDescriptionSidebar({
    resumeId,
    onKeywordsExtracted,
    jobDescription,
    onJobDescriptionChange,
}: JobDescriptionSidebarProps) {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
    const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null);

    const analyzeJobDescription = async () => {
        if (!jobDescription.trim()) return;

        setIsAnalyzing(true);
        try {
            const response = await axios.post(`${API_URL}/api/job/analyze`, {
                job_description: jobDescription,
                resume_id: resumeId,
            });

            setJobAnalysis(response.data.job_analysis);
            setGapAnalysis(response.data.gap_analysis);

            if (onKeywordsExtracted && response.data.job_analysis) {
                onKeywordsExtracted(response.data.job_analysis.required_keywords);
            }
        } catch (error) {
            console.error('Analysis failed:', error);
            alert('Failed to analyze job description');
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-white border-l border-gray-200">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold">Job Description Analysis</h2>
                <p className="text-sm text-gray-500 mt-1">
                    Paste a job description to optimize your resume
                </p>
            </div>

            {/* Input Area */}
            <div className="p-4 border-b border-gray-200">
                <textarea
                    value={jobDescription}
                    onChange={(e) => {
                        onJobDescriptionChange(e.target.value);
                    }}
                    placeholder="Paste job description here..."
                    className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <button
                    onClick={analyzeJobDescription}
                    disabled={isAnalyzing || !jobDescription.trim()}
                    className="mt-2 w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium"
                >
                    {isAnalyzing ? 'Analyzing...' : '🔍 Analyze'}
                </button>
            </div>

            {/* Results */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {jobAnalysis && (
                    <>
                        {/* Role Info */}
                        <div>
                            <h3 className="font-medium text-sm text-gray-700 mb-2">
                                Role Information
                            </h3>
                            <div className="space-y-1 text-sm">
                                <div>
                                    <span className="text-gray-500">Level:</span>{' '}
                                    <span className="font-medium">{jobAnalysis.role_level}</span>
                                </div>
                                <div>
                                    <span className="text-gray-500">Industry:</span>{' '}
                                    <span className="font-medium">{jobAnalysis.industry}</span>
                                </div>
                            </div>
                        </div>

                        {/* Required Keywords */}
                        <div>
                            <h3 className="font-medium text-sm text-gray-700 mb-2">
                                🔴 Required Keywords
                            </h3>
                            <div className="flex flex-wrap gap-1">
                                {jobAnalysis.required_keywords.map((keyword, idx) => (
                                    <span
                                        key={idx}
                                        className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium"
                                    >
                                        {keyword}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Preferred Keywords */}
                        {jobAnalysis.preferred_keywords.length > 0 && (
                            <div>
                                <h3 className="font-medium text-sm text-gray-700 mb-2">
                                    🟡 Preferred Keywords
                                </h3>
                                <div className="flex flex-wrap gap-1">
                                    {jobAnalysis.preferred_keywords.map((keyword, idx) => (
                                        <span
                                            key={idx}
                                            className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs font-medium"
                                        >
                                            {keyword}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Gap Analysis */}
                        {gapAnalysis && (
                            <>
                                {/* Alignment Score */}
                                <div>
                                    <h3 className="font-medium text-sm text-gray-700 mb-2">
                                        📊 Alignment Score
                                    </h3>
                                    <div className="flex items-center gap-2">
                                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full ${gapAnalysis.alignment_score >= 80
                                                    ? 'bg-green-500'
                                                    : gapAnalysis.alignment_score >= 60
                                                        ? 'bg-yellow-500'
                                                        : 'bg-red-500'
                                                    }`}
                                                style={{ width: `${gapAnalysis.alignment_score}%` }}
                                            />
                                        </div>
                                        <span className="text-sm font-medium">
                                            {gapAnalysis.alignment_score.toFixed(0)}%
                                        </span>
                                    </div>
                                </div>

                                {/* Missing Keywords */}
                                {gapAnalysis.missing_keywords.length > 0 && (
                                    <div>
                                        <h3 className="font-medium text-sm text-gray-700 mb-2">
                                            ⚠️ Missing Keywords
                                        </h3>
                                        <div className="flex flex-wrap gap-1">
                                            {gapAnalysis.missing_keywords.map((keyword, idx) => (
                                                <span
                                                    key={idx}
                                                    className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium"
                                                >
                                                    {keyword}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Weak Bullets */}
                                {gapAnalysis.weak_bullets.length > 0 && (
                                    <div>
                                        <h3 className="font-medium text-sm text-gray-700 mb-2">
                                            💡 Weak Bullets to Improve
                                        </h3>
                                        <div className="space-y-2">
                                            {gapAnalysis.weak_bullets.slice(0, 3).map((bullet, idx) => (
                                                <div
                                                    key={idx}
                                                    className="p-2 bg-yellow-50 border border-yellow-200 rounded text-xs"
                                                >
                                                    <div className="font-medium text-yellow-900">
                                                        "{bullet.bullet_text}"
                                                    </div>
                                                    <div className="text-yellow-700 mt-1">
                                                        {bullet.reason}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Recommendations */}
                                {gapAnalysis.recommendations.length > 0 && (
                                    <div>
                                        <h3 className="font-medium text-sm text-gray-700 mb-2">
                                            ✅ Recommendations
                                        </h3>
                                        <ul className="space-y-1 text-xs text-gray-600">
                                            {gapAnalysis.recommendations.map((rec, idx) => (
                                                <li key={idx} className="flex items-start gap-2">
                                                    <span className="text-blue-500">•</span>
                                                    <span>{rec}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
