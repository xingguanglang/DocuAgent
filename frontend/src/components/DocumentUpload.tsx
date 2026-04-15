import { useCallback, useState } from "react";
import { uploadDocument } from "../services/api";
import type { ToastMessage } from "./Toast";

const ALLOWED_EXTENSIONS = [".pdf", ".md", ".txt"];
const MAX_FILE_SIZE_MB = 50;

interface DocumentUploadProps {
  onToast: (type: ToastMessage["type"], text: string) => void;
}

export function DocumentUpload({ onToast }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState("");

  const validateFile = useCallback(
    (file: File): string | null => {
      const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        return `"${file.name}" is not supported. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}`;
      }
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        return `"${file.name}" is too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Max: ${MAX_FILE_SIZE_MB}MB`;
      }
      return null;
    },
    [],
  );

  const handleFiles = useCallback(
    async (files: FileList) => {
      const fileArray = Array.from(files);
      if (fileArray.length === 0) return;

      // Validate all files first
      const errors: string[] = [];
      const validFiles: File[] = [];
      for (const file of fileArray) {
        const error = validateFile(file);
        if (error) {
          errors.push(error);
        } else {
          validFiles.push(file);
        }
      }

      // Show validation errors
      for (const err of errors) {
        onToast("error", err);
      }

      if (validFiles.length === 0) return;

      setUploading(true);
      let successCount = 0;
      let failCount = 0;

      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];
        setUploadProgress(`Uploading ${i + 1}/${validFiles.length}: ${file.name}`);
        try {
          await uploadDocument(file);
          successCount++;
        } catch (err) {
          failCount++;
          const message = err instanceof Error ? err.message : "Upload failed";
          onToast("error", `Failed to upload "${file.name}": ${message}`);
        }
      }

      setUploading(false);
      setUploadProgress("");

      if (successCount > 0) {
        onToast(
          "success",
          successCount === 1
            ? `"${validFiles[0].name}" uploaded successfully`
            : `${successCount} files uploaded successfully`,
        );
      }
    },
    [onToast, validateFile],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files.length) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles],
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
        isDragging
          ? "border-blue-500 bg-blue-50"
          : uploading
            ? "border-green-400 bg-green-50"
            : "border-gray-300"
      }`}
    >
      {uploading ? (
        <div className="flex flex-col items-center gap-2">
          <svg
            className="h-5 w-5 animate-spin text-green-500"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <p className="text-sm text-green-600">{uploadProgress}</p>
        </div>
      ) : (
        <>
          <svg
            className="mx-auto mb-2 h-8 w-8 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-sm text-gray-500">Drag & drop files here, or</p>
          <label className="mt-2 inline-block cursor-pointer rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
            Browse files
            <input
              type="file"
              className="hidden"
              multiple
              accept=".pdf,.md,.txt"
              onChange={(e) => e.target.files && handleFiles(e.target.files)}
            />
          </label>
          <p className="mt-2 text-xs text-gray-400">PDF, Markdown, TXT (max {MAX_FILE_SIZE_MB}MB)</p>
        </>
      )}
    </div>
  );
}
