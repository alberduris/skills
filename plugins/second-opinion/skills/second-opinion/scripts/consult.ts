#!/usr/bin/env tsx

import { readFileSync } from 'fs';
import { resolve } from 'path';
import OpenAI from 'openai';

interface Args {
  message: string;
  files?: string[];
}

function parseArgs(): Args {
  const args = process.argv.slice(2);
  let message = '';
  let files: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--message' && args[i + 1]) {
      message = args[i + 1];
      i++;
    } else if (args[i] === '--files' && args[i + 1]) {
      files = args[i + 1].split(',').map(f => f.trim());
      i++;
    }
  }

  if (!message) {
    console.error('Error: --message required');
    process.exit(1);
  }

  return { message, files };
}

function buildPrompt(message: string, files?: string[]): string {
  let prompt = message;

  if (files && files.length > 0) {
    prompt += '\n\n---\n\n# Context Files\n\n';

    for (const filePath of files) {
      try {
        const absolutePath = resolve(filePath);
        const content = readFileSync(absolutePath, 'utf-8');
        prompt += `\n## ${filePath}\n\n\`\`\`\n${content}\n\`\`\`\n\n`;
      } catch (error) {
        console.error(`Warning: Could not read file ${filePath}:`, error instanceof Error ? error.message : error);
      }
    }
  }

  return prompt;
}

async function main() {
  const { message, files } = parseArgs();

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error('Error: OPENAI_API_KEY environment variable not set');
    process.exit(1);
  }

  const model = process.env.SECOND_OPINION_MODEL || 'gpt-5-pro-2025-10-06';
  const timeoutMs = parseInt(process.env.SECOND_OPINION_TIMEOUT || '1800000', 10); // 30min default
  const client = new OpenAI({ apiKey, timeout: timeoutMs });

  const prompt = buildPrompt(message, files);

  try {
    const response = await client.responses.create({
      model,
      input: [
        {
          role: 'developer',
          content: 'Peer SWE consultant; use web search when helpful.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      text: {
        format: {
          type: 'text'
        }
      },
      reasoning: {
        summary: 'auto'
      },
      tools: [
        {
          type: 'web_search',
          user_location: {
            type: 'approximate'
          },
          search_context_size: 'medium'
        }
      ],
      store: false,
      include: [
        'reasoning.encrypted_content',
        'web_search_call.action.sources'
      ]
    });

    console.log('\n=== PEER CONSULTANT RESPONSE ===\n');

    // Extract reasoning summary
    if (response.reasoning?.summary === 'detailed') {
      const reasoningOutput = response.output?.find((o: any) => o.type === 'reasoning');
      if (reasoningOutput?.summary) {
        console.log('## Reasoning\n');
        for (const item of reasoningOutput.summary) {
          if (item.type === 'summary_text') {
            console.log(item.text);
            console.log('');
          }
        }
        console.log('---\n');
      }
    }

    // Extract response text
    console.log('## Response\n');
    const responseText = response.output_text ||
                        response.output?.find((o: any) => o.type === 'message')?.content?.[0]?.text ||
                        'No response generated';
    console.log(responseText);

    // Extract web search sources if present
    const webSearchOutput = response.output?.find((o: any) => o.type === 'web_search');
    if (webSearchOutput?.action?.sources) {
      console.log('\n## Sources Used\n');
      webSearchOutput.action.sources.forEach((source: { url: string; title?: string }) => {
        console.log(`- ${source.title || source.url}`);
        console.log(`  ${source.url}`);
      });
    }

  } catch (error) {
    console.error('Error calling peer consultant:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
