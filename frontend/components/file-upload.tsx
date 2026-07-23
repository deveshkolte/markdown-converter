"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Upload } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConvertResult {
  markdown: string;
  fileName: string;
}

interface ConvertError {
  error: string;
}

interface FileUploadProps {
  onConvert: (result: ConvertResult | ConvertError) => void;
}

const ALLOWED_EXTENSIONS = [
  ".pdf",
  ".docx",
  ".pptx",
  ".xlsx",
  ".csv",
  ".html",
  ".htm",
  ".epub",
  ".txt",
  ".md",
];

export function FileUpload({ onConvert }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [coldStart, setColdStart] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const coldTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) processFile(file);
    },
    [],
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) processFile(file);
    },
    [],
  );

  useEffect(() => {
    return () => {
      if (coldTimerRef.current) clearTimeout(coldTimerRef.current);
    };
  }, []);

  async function processFile(file: File) {
    setError(null);
    setColdStart(false);

    const ext = "." + (file.name.split(".").pop() ?? "").toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported file type: ${ext}`);
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError("File too large. Maximum size is 50MB.");
      return;
    }

    setIsUploading(true);

    coldTimerRef.current = setTimeout(() => {
      setColdStart(true);
    }, 5_000);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiUrl}/convert`, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();

      if (result.markdown) {
        onConvert({ markdown: result.markdown, fileName: file.name });
      } else {
        onConvert({ error: result.error ?? "Conversion failed" });
      }
    } catch {
      setError("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      setColdStart(false);
      if (coldTimerRef.current) clearTimeout(coldTimerRef.current);
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      className={cn(
        "relative cursor-pointer rounded-xl border-2 border-dashed p-12 text-center transition-all",
        isDragging
          ? "border-primary bg-primary/5 scale-[1.02]"
          : "border-muted-foreground/25 hover:border-muted-foreground/50",
        isUploading && "pointer-events-none opacity-60",
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_EXTENSIONS.join(",")}
        className="hidden"
        onChange={handleFileSelect}
      />

      {isUploading ? (
        <div className="flex flex-col items-center gap-3">
          <div className="size-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Converting…</p>
          {coldStart && (
            <p className="text-xs text-amber-600 dark:text-amber-400">
              Waking up the server — this can take up to a minute on the first request.
            </p>
          )}
        </div>
      ) : (
        <>
          <div className="mx-auto mb-4 flex size-14 items-center justify-center rounded-full bg-muted">
            <Upload
              className={cn(
                "size-7 transition-colors",
                isDragging
                  ? "text-primary"
                  : "text-muted-foreground",
              )}
            />
          </div>
          <p className="text-base font-medium">
            {isDragging
              ? "Drop your file here"
              : "Drop a document to convert"}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            or{" "}
            <span className="font-medium text-primary underline underline-offset-2">
              browse files
            </span>
          </p>
          <p className="mt-4 text-xs text-muted-foreground">
            PDF, DOCX, PPTX, XLSX, CSV, HTML, EPUB, TXT, MD &mdash; Up to 50MB
          </p>
        </>
      )}

      {error && (
        <div className="absolute bottom-4 left-4 right-4 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}
    </div>
  );
}
