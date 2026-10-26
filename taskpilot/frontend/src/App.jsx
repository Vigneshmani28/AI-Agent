import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = "http://localhost:8002/api/v1/agent/chat";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "agent", text: "Hi! I'm TaskPilot. Try “Add a task: buy groceries” or “Show my tasks”." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "agent", text: data.response, tools: data.tools_used },
      ]);
    } catch (err) {
      setMessages((m) => [...m, { role: "agent", text: `Error: ${err.message}`, error: true }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>TaskPilot</header>
      <main>
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}${m.error ? " error" : ""}`}>
            <div className="bubble">
              {m.role === "agent" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.text}</ReactMarkdown>
              ) : (
                m.text
              )}
            </div>
            {m.tools?.length > 0 && (
              <details className="tools">
                <summary>Tools used: {m.tools.map((t) => t.tool).join(", ")}</summary>
                <pre>{JSON.stringify(m.tools, null, 2)}</pre>
              </details>
            )}
          </div>
        ))}
        {loading && <div className="msg agent"><div className="bubble typing">Thinking…</div></div>}
        <div ref={bottomRef} />
      </main>
      <form onSubmit={send}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask TaskPilot to manage your tasks…"
          autoFocus
        />
        <button disabled={loading || !input.trim()}>Send</button>
      </form>
    </div>
  );
}
