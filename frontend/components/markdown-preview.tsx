"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Download, ArrowLeft, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface MarkdownPreviewProps {
  markdown: string;
  fileName: string;
  onReset: () => void;
}

export function MarkdownPreview({
  markdown,
  fileName,
  onReset,
}: MarkdownPreviewProps) {
  const [copied, setCopied] = useState(false);
  const [view, setView] = useState<"rendered" | "raw">("rendered");

  const handleCopy = async () => {
    await navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName.replace(/\.[^/.]+$/, "") + ".md";
    a.click();
    URL.revokeObjectURL(url);
  };

  const lineCount = markdown.split("\n").length;
  const charCount = markdown.length;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="size-5 text-muted-foreground shrink-0" />
          <div>
            <p className="font-medium leading-tight">{fileName}</p>
            <p className="text-xs text-muted-foreground">
              {lineCount} lines &middot; {charCount.toLocaleString()} characters
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 rounded-lg border p-0.5">
          <button
            type="button"
            onClick={() => setView("rendered")}
            className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
              view === "rendered"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Preview
          </button>
          <button
            type="button"
            onClick={() => setView("raw")}
            className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
              view === "raw"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Raw
          </button>
        </div>
      </div>

      <ScrollArea className="h-[55vh] rounded-lg border bg-muted/30 p-5">
        {view === "rendered" ? (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {markdown}
            </ReactMarkdown>
          </div>
        ) : (
          <pre className="text-sm font-mono whitespace-pre-wrap">{markdown}</pre>
        )}
      </ScrollArea>

      <div className="flex items-center justify-between">
        <Button variant="outline" size="sm" onClick={onReset}>
          <ArrowLeft className="size-4" />
          Convert another
        </Button>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? (
              <>
                <Check className="size-4 text-green-500" />
                Copied
              </>
            ) : (
              <>
                <Copy className="size-4" />
                Copy
              </>
            )}
          </Button>
          <Button size="sm" onClick={handleDownload}>
            <Download className="size-4" />
            Download .md
          </Button>
        </div>
      </div>
    </div>
  );
}
