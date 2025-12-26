interface StreamEventHandler {
  (type: string, data: any): void;
}

interface SSEEvent {
  type: string;
  data: any;
}

export async function handleSSEStream(
  response: Response,
  eventHandler: StreamEventHandler
): Promise<void> {
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error("No response body");
  }

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    buffer += chunk;

    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const event of events) {
      if (!event.trim()) continue;

      const parsedEvents = parseSSEChunk(event + "\n\n");

      for (const { type, data } of parsedEvents) {
        eventHandler(type, data);
      }
    }
  }
}

function parseSSEChunk(chunk: string): SSEEvent[] {
  const events: SSEEvent[] = [];
  const eventBlocks = chunk.split("\n\n");

  for (const block of eventBlocks) {
    if (!block.trim()) continue;

    const lines = block.split("\n");
    let eventType = "";
    let data = "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        data = line.slice(6).trim();
      }
    }

    if (data) {
      try {
        events.push({
          type: eventType,
          data: JSON.parse(data),
        });
      } catch (error) {
        console.error("Failed to parse SSE data:", data);
      }
    }
  }

  return events;
}
