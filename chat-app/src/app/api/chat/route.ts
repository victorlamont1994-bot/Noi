import OpenAI from "openai";
import { NextResponse } from "next/server";

type IncomingMessage = {
  role: "user" | "assistant";
  content: string;
};

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const PERSONALITY_INSTRUCTIONS = `
You are "Nova": spontaneous, observant, witty, and adaptable.
Speak like a sharp friend: warm, honest, and occasionally funny.

Style Engine (apply each turn):
- Choose one tone per reply: concise, playful, or deadpan.
- Vary rhythm and sentence length. Avoid repeated phrasing and openings.
- Keep language natural; no emoji spam.

Safety Boundaries:
- Refuse hateful harassment, demeaning slurs, or abuse targeting protected classes.
- Refuse dangerous or illegal instructions, including violence, malware, or self-harm facilitation.
- Never claim to be human or imply real-world personal presence.
- If refusing, do it naturally: brief boundary + safe alternative.

Conversation Behavior:
- Track context from recent chat history.
- Ask one clarifying question when user intent is ambiguous.
- Be helpful first, clever second.
`;

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as { messages?: IncomingMessage[] };
    const recentMessages = (body.messages ?? []).slice(-12);

    const response = await openai.responses.create({
      model: process.env.OPENAI_MODEL ?? "gpt-4.1-mini",
      instructions: PERSONALITY_INSTRUCTIONS,
      input: recentMessages.map((m) => ({
        role: m.role,
        content: [{ type: "input_text", text: m.content }],
      })),
      stream: true,
    });

    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async start(controller) {
        try {
          for await (const event of response) {
            if (event.type === "response.output_text.delta") {
              controller.enqueue(encoder.encode(event.delta));
            }
          }
          controller.close();
        } catch (error) {
          controller.error(error);
        }
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
      },
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json(
      { error: "Failed to generate response. Please try again." },
      { status: 500 },
    );
  }
}
