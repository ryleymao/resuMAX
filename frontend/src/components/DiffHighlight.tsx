/**
 * DiffHighlight Component
 * Shows text differences with color highlighting
 * Yellow = changed, Green = added, Red = removed
 */

interface DiffHighlightProps {
    original: string;
    modified: string;
    showOriginal?: boolean;
}

interface Change {
    type: 'added' | 'removed' | 'unchanged';
    text: string;
}

export function DiffHighlight({
    original,
    modified,
    showOriginal = false,
}: DiffHighlightProps) {
    const changes = computeDiff(original, modified);

    return (
        <div className="space-y-2">
            {showOriginal && (
                <div className="text-sm text-gray-500">
                    <span className="font-medium">Original:</span>
                    <div className="mt-1 p-2 bg-gray-50 rounded">{original}</div>
                </div>
            )}

            <div className="text-sm">
                <span className="font-medium">Modified:</span>
                <div className="mt-1 p-2 bg-white rounded border border-gray-200">
                    {changes.map((change, idx) => (
                        <span
                            key={idx}
                            className={
                                change.type === 'added'
                                    ? 'bg-yellow-200 text-yellow-900 font-medium'
                                    : change.type === 'removed'
                                        ? 'bg-red-100 text-red-600 line-through opacity-60'
                                        : 'text-gray-700'
                            }
                        >
                            {change.text}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}

/**
 * Improved word-level diff algorithm
 * Highlights changed words in yellow, keeps unchanged words normal
 */
function computeDiff(original: string, modified: string): Change[] {
    if (original === modified) {
        return [{ type: 'unchanged', text: original }];
    }

    const originalWords = original.split(/\s+/);
    const modifiedWords = modified.split(/\s+/);
    const changes: Change[] = [];

    // Simple longest common subsequence approach
    let origIdx = 0;
    let modIdx = 0;

    while (origIdx < originalWords.length || modIdx < modifiedWords.length) {
        if (origIdx >= originalWords.length) {
            // Only modified words left
            changes.push({ type: 'added', text: modifiedWords[modIdx] + ' ' });
            modIdx++;
        } else if (modIdx >= modifiedWords.length) {
            // Only original words left (removed)
            changes.push({ type: 'removed', text: originalWords[origIdx] + ' ' });
            origIdx++;
        } else if (originalWords[origIdx] === modifiedWords[modIdx]) {
            // Words match
            changes.push({ type: 'unchanged', text: originalWords[origIdx] + ' ' });
            origIdx++;
            modIdx++;
        } else {
            // Words differ - check if next word in original matches current in modified
            if (origIdx + 1 < originalWords.length && originalWords[origIdx + 1] === modifiedWords[modIdx]) {
                // Word was removed from original
                changes.push({ type: 'removed', text: originalWords[origIdx] + ' ' });
                origIdx++;
            } else if (modIdx + 1 < modifiedWords.length && originalWords[origIdx] === modifiedWords[modIdx + 1]) {
                // Word was added to modified
                changes.push({ type: 'added', text: modifiedWords[modIdx] + ' ' });
                modIdx++;
            } else {
                // Both changed
                changes.push({ type: 'removed', text: originalWords[origIdx] + ' ' });
                changes.push({ type: 'added', text: modifiedWords[modIdx] + ' ' });
                origIdx++;
                modIdx++;
            }
        }
    }

    return changes;
}
