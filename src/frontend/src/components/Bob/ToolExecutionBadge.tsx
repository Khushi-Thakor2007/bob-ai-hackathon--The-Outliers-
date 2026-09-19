interface ToolExecutionBadgeProps {
  toolName: string;
  resultSummary?: string;
}

export default function ToolExecutionBadge({ toolName, resultSummary }: ToolExecutionBadgeProps) {
  return (
    <div className="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs">
      <span className="text-blue-400 font-mono">⚙ {toolName}</span>
      {resultSummary && <span className="text-gray-500">{String(resultSummary).slice(0, 60)}</span>}
    </div>
  );
}
