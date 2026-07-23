"use client";

import { useState } from "react";
import { FileUpload } from "@/components/file-upload";
import { MarkdownPreview } from "@/components/markdown-preview";

interface ConvertResult {
  markdown: string;
  fileName: string;
}

interface ConvertError {
  error: string;
}

type ConvertData = ConvertResult | ConvertError;

export default function Home() {
  const [data, setData] = useState<ConvertData | null>(null);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="mx-auto flex h-14 max-w-4xl items-center px-4">
          <span className="font-medium">Markdown Converter</span>
        </div>
      </header>

      <main className="flex-1">
        <section className="mx-auto max-w-2xl px-4 pt-20 pb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Convert Any Document to
            <br />
            <span className="text-primary">Clean Markdown</span>
          </h1>
          <p className="mt-4 text-lg text-muted-foreground/80">
            Perfect for LLM workflows, RAG pipelines, note-taking, and documentation.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {["PDF", "DOCX", "PPTX", "XLSX", "EPUB", "HTML", "CSV", "TXT", "MD"].map(
              (fmt) => (
                <span
                  key={fmt}
                  className="inline-flex items-center rounded-full border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground"
                >
                  {fmt}
                </span>
              ),
            )}
          </div>
        </section>

        <section className="mx-auto max-w-lg px-4 pb-20">
          {!data ? (
            <FileUpload onConvert={setData} />
          ) : "error" in data ? (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center text-sm text-destructive">
              {data.error}
              <button
                type="button"
                className="ml-2 font-medium underline underline-offset-2"
                onClick={() => setData(null)}
              >
                Try again
              </button>
            </div>
          ) : (
            <MarkdownPreview
              markdown={data.markdown}
              fileName={data.fileName}
              onReset={() => setData(null)}
            />
          )}
        </section>
      </main>

      <footer className="border-t py-6 text-center text-sm text-muted-foreground">
        Powered by{" "}
        <a
          href="https://github.com/deveshkolte/markdown-converter"
          className="underline underline-offset-2 hover:text-foreground"
        >
          markdown-converter
        </a>
        {" "}&mdash;{" "}
        <a
          href="https://github.com/deveshkolte/markdown-converter"
          className="underline underline-offset-2 hover:text-foreground"
        >
          GitHub
        </a>
      </footer>
    </div>
  );
}
