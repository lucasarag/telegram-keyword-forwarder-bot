export default function LogViewer({ logs }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-6 w-[600px] mt-6 h-[400px] overflow-y-scroll">
      <h2 className="text-xl font-semibold mb-3">Logs</h2>
      <div className="text-sm space-y-1 font-mono">
        {logs.length === 0 ? (
          <p className="text-gray-500">Sem logs ainda...</p>
        ) : (
          logs.map((log, i) => <div key={i}>{log}</div>)
        )}
      </div>
    </div>
  );
}
