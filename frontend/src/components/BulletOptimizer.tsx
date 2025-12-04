/**
 * Bullet Optimizer Component
 * Shows original vs optimized bullet with accept/reject controls
 */
import { useState } from 'react';
import axios from 'axios';
import { DiffHighlight } from './DiffHighlight';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface BulletOptimizerProps {
    bullet: string;
    context?: {
        job_title?: string;
        company?: string;
    };
    onAccept: (optimizedBullet: string) => void;
    onReject: () => void;
}

export function BulletOptimizer({
    bullet,
    context = {},
    onAccept,
    onReject,
}: BulletOptimizerProps) {
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [optimizedBullet, setOptimizedBullet] = useState<string | null>(null);

    const optimize = async () => {
        setIsOptimizing(true);
        try {
            const response = await axios.post(`${API_URL}/api/optimize/bullet`, {
                bullet,
                context,
            });

            setOptimizedBullet(response.data.optimized);
        } catch (error) {
            console.error('Optimization failed:', error);
            alert('Failed to optimize bullet');
        } finally {
            setIsOptimizing(false);
        }
    };

    const handleAccept = () => {
        if (optimizedBullet) {
            onAccept(optimizedBullet);
            setOptimizedBullet(null);
        }
    };

    const handleReject = () => {
        setOptimizedBullet(null);
        onReject();
    };

    if (optimizedBullet) {
        return (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-3">
                <div className="flex items-start justify-between">
                    <h4 className="font-medium text-blue-900">AI Suggestion</h4>
                    <div className="flex gap-2">
                        <button
                            onClick={handleAccept}
                            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                        >
                            ✓ Accept
                        </button>
                        <button
                            onClick={handleReject}
                            className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                        >
                            ✗ Reject
                        </button>
                    </div>
                </div>

                <DiffHighlight original={bullet} modified={optimizedBullet} showOriginal />
            </div>
        );
    }

    return (
        <button
            onClick={optimize}
            disabled={isOptimizing}
            className="text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400"
        >
            {isOptimizing ? '✨ Optimizing...' : '✨ Optimize with AI'}
        </button>
    );
}
