export default function ConfigPanel({ keyword, chatId, setKeyword, setChatId, handleConfig }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-6 w-96 mt-6">
      <h2 className="text-xl font-semibold mb-3">Configuração</h2>
      <input
        className="input"
        placeholder="Keyword"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />
      <input
        className="input"
        placeholder="Chat ID"
        value={chatId}
        onChange={(e) => setChatId(e.target.value)}
      />
      <button className="btn-primary mt-4 w-full" onClick={handleConfig}>
        Salvar Configurações
      </button>
    </div>
  );
}
