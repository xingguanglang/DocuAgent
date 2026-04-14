import { useCallback, useState } from "react";
import { uploadDocument } from "../services/api";

export function DocumentUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFiles = useCallback(async (files: FileList) => {
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await uploadDocument(file);
      }
    } catch {
      // TODO: Show error toast
    } finally {
      setUploading(false);
    }
  }, []);

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
        isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300"
      }`}
    >
      <p className="text-sm text-gray-500">
        {uploading ? "Uploading..." : "Drag & drop files here, or"}
      </p>
      {!uploading && (
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
      )}
    </div>
  );
}
