import { useRef } from "react";

export default function Dropzone({ onFileSelected, disabled }) {
  const inputRef = useRef(null);

  const handleClick = () => {
    if (!disabled) inputRef.current.click();
  };

  const handleFile = (file) => {
    if (file && file.name.endsWith(".csv")) {
      onFileSelected(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div
      onClick={handleClick}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className={`w-[70%] mx-auto mt-10 p-10
        border-2 border-dashed rounded-2xl
        transition-all cursor-pointer
        ${
          disabled
            ? "opacity-40 cursor-not-allowed"
            : "hover:border-blue-400 hover:bg-white/5"
        }
      `}
    >
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="text-5xl">📄</div>

        <p className="text-xl font-semibold">
          Arrastra tu archivo CSV o haz clic para cargarlo
        </p>

        <p className="text-sm opacity-70">
          Solo archivos <b>.csv</b>
        </p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        hidden
        onChange={(e) => handleFile(e.target.files[0])}
      />
    </div>
  );
}
